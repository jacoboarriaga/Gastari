from flask import jsonify, request, send_from_directory, current_app
from flask_login import login_required, current_user
from datetime import date
import datetime as dt
from sqlalchemy import func
from app import db
from app.models import Transaction, Account, Category
from app.routes import api_bp


@api_bp.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@api_bp.route("/chart/monthly-summary")
@login_required
def monthly_summary():
    year = request.args.get("year", date.today().year, type=int)
    month = request.args.get("month", date.today().month, type=int)

    if month == 12:
        me = date(year + 1, 1, 1) - dt.timedelta(days=1)
    else:
        me = date(year, month + 1, 1) - dt.timedelta(days=1)
    ms = date(year, month, 1)

    inc = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "income",
            Transaction.date >= ms,
            Transaction.date <= me,
        )
        .scalar()
    )
    exp = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense",
            Transaction.date >= ms,
            Transaction.date <= me,
        )
        .scalar()
    )
    return jsonify({"income": float(inc), "expenses": float(exp)})


@api_bp.route("/chart/expense-categories")
@login_required
def expense_categories():
    year = request.args.get("year", date.today().year, type=int)
    month = request.args.get("month", date.today().month, type=int)

    if month == 12:
        me = date(year + 1, 1, 1) - dt.timedelta(days=1)
    else:
        me = date(year, month + 1, 1) - dt.timedelta(days=1)
    ms = date(year, month, 1)

    data = (
        db.session.query(Category.name, Category.color, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense",
            Transaction.date >= ms,
            Transaction.date <= me,
        )
        .group_by(Category.id)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    return jsonify([{"name": n, "color": c, "amount": float(a)} for n, c, a in data])
