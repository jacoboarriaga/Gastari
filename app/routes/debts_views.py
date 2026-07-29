from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import date
import os
import uuid

from app import db
from app.models import Debt, Transaction, Account, Category
from app.forms import DebtForm
from app.routes import debts_bp

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_attachment(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        return filename
    return None


@debts_bp.route("/")
@login_required
def index():
    debt_type = request.args.get("type", "")
    search_query = request.args.get("q", "").strip()
    query = Debt.query.filter_by(user_id=current_user.id, is_active=True)
    if debt_type:
        query = query.filter_by(debt_type=debt_type)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(Debt.name.ilike(like))
    debts = query.order_by(Debt.created_at.desc()).all()
    total_owed = sum(d.current_amount for d in debts)
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    return render_template("debts/index.html", debts=debts, total_owed=total_owed, accounts=accounts, debt_type=debt_type, search_query=search_query)


@debts_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = DebtForm()
    if form.validate_on_submit():
        debt = Debt(
            user_id=current_user.id,
            name=form.name.data.strip(),
            debt_type=form.debt_type.data,
            original_amount=round(form.original_amount.data, 2),
            current_amount=round(form.current_amount.data, 2),
            interest_rate=form.interest_rate.data or 0.0,
            minimum_payment=round(form.minimum_payment.data, 2) if form.minimum_payment.data else None,
            due_day=form.due_day.data if form.due_day.data else None,
            creditor=form.creditor.data.strip() if form.creditor.data else None,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
        )
        db.session.add(debt)
        db.session.commit()
        flash("Deuda registrada.", "success")
        return redirect(url_for("debts.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("debts/add.html", form=form)


@debts_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    debt = Debt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = DebtForm(obj=debt)
    if form.validate_on_submit():
        debt.name = form.name.data.strip()
        debt.debt_type = form.debt_type.data
        debt.original_amount = round(form.original_amount.data, 2)
        debt.current_amount = round(form.current_amount.data, 2)
        debt.interest_rate = form.interest_rate.data or 0.0
        debt.minimum_payment = round(form.minimum_payment.data, 2) if form.minimum_payment.data else None
        debt.due_day = form.due_day.data if form.due_day.data else None
        debt.creditor = form.creditor.data.strip() if form.creditor.data else None
        debt.start_date = form.start_date.data
        debt.end_date = form.end_date.data
        if debt.current_amount <= 0:
            debt.is_active = False
        db.session.commit()
        flash("Deuda actualizada.", "success")
        return redirect(url_for("debts.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("debts/edit.html", form=form, debt=debt)


@debts_bp.route("/<int:id>/pay", methods=["POST"])
@login_required
def pay(id):
    debt = Debt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount = round(request.form.get("amount", 0, type=float), 2)
    account_id = request.form.get("account_id", 0, type=int)

    if amount <= 0:
        flash("El monto debe ser mayor a 0.", "danger")
        return redirect(url_for("debts.index"))

    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        flash("Selecciona una cuenta valida.", "danger")
        return redirect(url_for("debts.index"))

    if account.balance < amount:
        flash("Saldo insuficiente en la cuenta.", "danger")
        return redirect(url_for("debts.index"))

    account.balance = round(account.balance - amount, 2)
    debt.current_amount = max(0, round(debt.current_amount - amount, 2))

    expense_cat = Category.query.filter_by(
        user_id=current_user.id, name="Pago de Tarjeta", category_type="expense"
    ).first()

    attachment = None
    receipt = request.files.get("receipt")
    if receipt and receipt.filename:
        attachment = save_attachment(receipt)

    transaction = Transaction(
        user_id=current_user.id,
        account_id=account.id,
        category_id=expense_cat.id if expense_cat else None,
        transaction_type="expense",
        amount=amount,
        description=f"Pago deuda: {debt.name}",
        date=date.today(),
        debt_id=debt.id,
        notes=request.form.get("notes", ""),
        attachment_path=attachment,
    )
    db.session.add(transaction)

    if debt.current_amount <= 0:
        debt.is_active = False
        flash("Deuda pagada completamente!", "success")
    else:
        flash(f"Pago de ${amount:,.2f} registrado. Se desconto de {account.name}.", "success")

    db.session.commit()
    return redirect(url_for("debts.index"))


@debts_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    debt = Debt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    debt.is_active = False
    db.session.commit()
    flash("Deuda eliminada.", "info")
    return redirect(url_for("debts.index"))
