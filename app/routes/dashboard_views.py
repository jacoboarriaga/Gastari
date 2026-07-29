from flask import render_template
from flask_login import login_required, current_user
from datetime import date
import datetime as dt
from sqlalchemy import func
from app import db
from app.models import Account, Transaction, Debt, Budget, Goal, Category
from app.routes import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    total_balance = sum(a.balance for a in accounts if a.account_type != "credit_card")
    today = date.today()
    month_start = today.replace(day=1)
    if month_start.month < 12:
        month_end = date(month_start.year, month_start.month + 1, 1) - dt.timedelta(days=1)
    else:
        month_end = date(month_start.year + 1, 1, 1) - dt.timedelta(days=1)

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
    monthly_savings = monthly_income - monthly_expenses

    recent_transactions = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(5)
        .all()
    )

    debts = Debt.query.filter_by(user_id=current_user.id, is_active=True).all()

    active_budgets = Budget.query.filter(
        Budget.user_id == current_user.id,
        Budget.is_active == True,
        Budget.start_date <= today,
        Budget.end_date >= today,
    ).all()

    daily_expenses = []
    for i in range(30, -1, -1):
        d = today - dt.timedelta(days=i)
        day_total = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "expense",
                Transaction.date == d,
            )
            .scalar()
        )
        daily_expenses.append({"date": d.strftime("%d/%m"), "amount": float(day_total)})

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

    return render_template(
        "dashboard/index.html",
        accounts=accounts,
        total_balance=total_balance,
        total_debt=0,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_savings=monthly_savings,
        recent_transactions=recent_transactions,
        debts=debts,
        total_owed=sum(d.current_amount for d in debts),
        active_budgets=active_budgets,
        goals=[],
        daily_expenses=daily_expenses,
        expense_by_category=expense_by_category,
        today=today,
    )
