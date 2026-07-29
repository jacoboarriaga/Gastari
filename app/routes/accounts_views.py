from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Account
from app.forms import AccountForm
from app.routes import accounts_bp


@accounts_bp.route("/")
@login_required
def index():
    account_type = request.args.get("type", "")
    search_query = request.args.get("q", "").strip()
    query = Account.query.filter_by(user_id=current_user.id, is_active=True)
    if account_type:
        query = query.filter_by(account_type=account_type)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(Account.name.ilike(like))
    accounts = query.order_by(Account.created_at.desc()).all()
    return render_template("accounts/index.html", accounts=accounts, account_type=account_type, search_query=search_query)


@accounts_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = AccountForm()
    if form.validate_on_submit():
        balance = round(form.balance.data or 0.0, 2)
        account = Account(
            user_id=current_user.id,
            name=form.name.data.strip(),
            account_type=form.account_type.data,
            balance=balance,
            currency=form.currency.data,
            color=form.color.data,
            icon=form.icon.data,
            credit_limit=form.credit_limit.data,
            closing_day=form.closing_day.data if form.closing_day.data else None,
            payment_day=form.payment_day.data if form.payment_day.data else None,
            interest_rate=form.interest_rate.data,
        )
        if form.account_type.data == "credit_card" and account.balance > 0:
            account.balance = -abs(account.balance)
        db.session.add(account)
        db.session.commit()
        flash("Cuenta creada correctamente.", "success")
        return redirect(url_for("accounts.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("accounts/add.html", form=form)


@accounts_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    account = Account.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = AccountForm(obj=account)
    if form.validate_on_submit():
        account.name = form.name.data.strip()
        account.account_type = form.account_type.data
        account.balance = round(form.balance.data or 0.0, 2)
        account.currency = form.currency.data
        account.color = form.color.data
        account.icon = form.icon.data
        account.credit_limit = form.credit_limit.data
        account.closing_day = form.closing_day.data if form.closing_day.data else None
        account.payment_day = form.payment_day.data if form.payment_day.data else None
        account.interest_rate = form.interest_rate.data
        if account.account_type == "credit_card" and account.balance > 0:
            account.balance = -abs(account.balance)
        db.session.commit()
        flash("Cuenta actualizada.", "success")
        return redirect(url_for("accounts.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("accounts/edit.html", form=form, account=account)


@accounts_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    account = Account.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    account.is_active = False
    db.session.commit()
    flash("Cuenta eliminada.", "info")
    return redirect(url_for("accounts.index"))
