from flask import render_template, request
from flask_login import login_required, current_user
from datetime import date
import datetime as dt
from sqlalchemy import func
from app import db
from app.models import Transaction, Account, Category
from app.routes import reports_bp


@reports_bp.route("/")
@login_required
def index():
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    if month == 12:
        month_end = date(year + 1, 1, 1) - dt.timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - dt.timedelta(days=1)
    month_start = date(year, month, 1)

    monthly_income = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "income",
            Transaction.date >= month_start,
            Transaction.date <= month_end,
        )
        .scalar()
    )
    monthly_expenses = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense",
            Transaction.date >= month_start,
            Transaction.date <= month_end,
        )
        .scalar()
    )

    expense_by_category_raw = (
        db.session.query(Category.name, Category.color, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense",
            Transaction.date >= month_start,
            Transaction.date <= month_end,
        )
        .group_by(Category.id)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    expense_by_category = [[row[0], row[1], float(row[2])] for row in expense_by_category_raw]

    daily_expenses = []
    for i in range(1, month_end.day + 1):
        d = date(year, month, i)
        day_total = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "expense",
                Transaction.date == d,
            )
            .scalar()
        )
        daily_expenses.append({"date": i, "amount": float(day_total)})

    account_balances = Account.query.filter_by(user_id=current_user.id, is_active=True).all()

    yearly_data = []
    for m in range(1, 13):
        if m == 12:
            ye = date(year + 1, 1, 1) - dt.timedelta(days=1)
        else:
            ye = date(year, m + 1, 1) - dt.timedelta(days=1)
        ys = date(year, m, 1)
        inc = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "income",
                Transaction.date >= ys,
                Transaction.date <= ye,
            )
            .scalar()
        )
        exp = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "expense",
                Transaction.date >= ys,
                Transaction.date <= ye,
            )
            .scalar()
        )
        yearly_data.append({"month": m, "income": float(inc), "expenses": float(exp)})

    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]

    return render_template(
        "reports/index.html",
        year=year,
        month=month,
        month_name=months[month - 1],
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        expense_by_category=expense_by_category,
        income_by_category=[],
        daily_expenses=daily_expenses,
        account_balances=account_balances,
        yearly_data=yearly_data,
        savings_rate=round(((monthly_income - monthly_expenses) / monthly_income * 100), 1) if monthly_income > 0 else 0,
    )
