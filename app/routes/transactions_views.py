from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import date
import os
import uuid
from app import db
from app.models import Transaction, Account, Category
from app.forms import TransactionForm, CategoryForm
from app.routes import transactions_bp

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


@transactions_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    type_filter = request.args.get("type", "")
    account_filter = request.args.get("account", 0, type=int)
    search_query = request.args.get("q", "").strip()

    query = Transaction.query.filter_by(user_id=current_user.id)
    if type_filter:
        query = query.filter_by(transaction_type=type_filter)
    if account_filter:
        query = query.filter_by(account_id=account_filter)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            db.or_(Transaction.description.ilike(like), Transaction.notes.ilike(like))
        )

    pagination = query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).paginate(page=page, per_page=20)
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "transactions/index.html",
        transactions=pagination.items,
        pagination=pagination,
        accounts=accounts,
        categories=categories,
        type_filter=type_filter,
        account_filter=account_filter,
        search_query=search_query,
    )


@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = TransactionForm()
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.account_id.choices = [(a.id, a.name) for a in accounts]
    form.category_id.choices = [(0, "-- Sin categoria --")] + [(c.id, c.name) for c in categories]
    form.to_account_id.choices = [(0, "-- Seleccionar --")] + [(a.id, a.name) for a in accounts]

    if request.method == "GET" and not form.is_submitted():
        form.date.data = date.today()
        tx_type = request.args.get("type", "expense")
        if tx_type in ("income", "expense", "transfer"):
            form.transaction_type.data = tx_type

    if form.validate_on_submit():
        if form.amount.data <= 0:
            flash("El monto debe ser mayor a 0.", "danger")
            return render_template("transactions/add.html", form=form)

        amount = round(form.amount.data, 2)

        if form.transaction_type.data == "transfer":
            if not form.to_account_id.data:
                flash("Selecciona una cuenta destino.", "danger")
                return render_template("transactions/add.html", form=form)
            if form.to_account_id.data == form.account_id.data:
                flash("No puedes transferir a la misma cuenta.", "danger")
                return render_template("transactions/add.html", form=form)

        transaction = Transaction(
            user_id=current_user.id,
            account_id=form.account_id.data,
            transaction_type=form.transaction_type.data,
            amount=amount,
            category_id=form.category_id.data if form.category_id.data else None,
            description=form.description.data.strip() if form.description.data else None,
            date=form.date.data,
            notes=form.notes.data,
            is_recurring=form.is_recurring.data,
            recurring_frequency=form.recurring_frequency.data if form.recurring_frequency.data else None,
        )

        receipt = request.files.get("receipt")
        if receipt and receipt.filename:
            transaction.attachment_path = save_attachment(receipt)

        account = Account.query.get(form.account_id.data)
        if form.transaction_type.data == "income":
            account.balance += amount
        elif form.transaction_type.data == "expense":
            account.balance -= amount
        elif form.transaction_type.data == "transfer":
            to_account = Account.query.get(form.to_account_id.data)
            account.balance -= amount
            to_account.balance += amount
            transaction.to_account_id = form.to_account_id.data

        db.session.add(transaction)
        db.session.commit()
        flash("Transaccion registrada.", "success")
        return redirect(url_for("transactions.index"))

    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("transactions/add.html", form=form)


@transactions_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.account_id.choices = [(a.id, a.name) for a in accounts]
    form.category_id.choices = [(0, "-- Sin categoria --")] + [(c.id, c.name) for c in categories]
    form.to_account_id.choices = [(0, "-- Seleccionar --")] + [(a.id, a.name) for a in accounts]

    if form.validate_on_submit():
        amount = round(form.amount.data, 2)

        old_account = Account.query.get(transaction.account_id)
        if transaction.transaction_type == "income":
            old_account.balance -= transaction.amount
        elif transaction.transaction_type == "expense":
            old_account.balance += transaction.amount
        elif transaction.transaction_type == "transfer" and transaction.to_account_id:
            old_to = Account.query.get(transaction.to_account_id)
            old_account.balance += transaction.amount
            old_to.balance -= transaction.amount

        transaction.account_id = form.account_id.data
        transaction.transaction_type = form.transaction_type.data
        transaction.amount = amount
        transaction.category_id = form.category_id.data if form.category_id.data else None
        transaction.description = form.description.data.strip() if form.description.data else None
        transaction.date = form.date.data
        transaction.notes = form.notes.data
        transaction.is_recurring = form.is_recurring.data
        transaction.recurring_frequency = form.recurring_frequency.data if form.recurring_frequency.data else None

        receipt = request.files.get("receipt")
        if receipt and receipt.filename:
            transaction.attachment_path = save_attachment(receipt)

        new_account = Account.query.get(form.account_id.data)
        if form.transaction_type.data == "income":
            new_account.balance += amount
        elif form.transaction_type.data == "expense":
            new_account.balance -= amount
        elif form.transaction_type.data == "transfer":
            to_account = Account.query.get(form.to_account_id.data)
            new_account.balance -= amount
            to_account.balance += amount
            transaction.to_account_id = form.to_account_id.data

        db.session.commit()
        flash("Transaccion actualizada.", "success")
        return redirect(url_for("transactions.index"))

    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("transactions/edit.html", form=form, transaction=transaction)


@transactions_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account = Account.query.get(transaction.account_id)
    if transaction.transaction_type == "income":
        account.balance -= transaction.amount
    elif transaction.transaction_type == "expense":
        account.balance += transaction.amount
    elif transaction.transaction_type == "transfer" and transaction.to_account_id:
        to_account = Account.query.get(transaction.to_account_id)
        account.balance += transaction.amount
        to_account.balance -= transaction.amount
    db.session.delete(transaction)
    db.session.commit()
    flash("Transaccion eliminada.", "info")
    return redirect(url_for("transactions.index"))
