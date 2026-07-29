from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from app import db
from app.models import Budget, Category
from app.forms import BudgetForm
from app.routes import budgets_bp


@budgets_bp.route("/")
@login_required
def index():
    today = date.today()
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")

    query = Budget.query.filter_by(user_id=current_user.id)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(Budget.name.ilike(like))

    budgets = query.order_by(Budget.created_at.desc()).all()

    if status_filter == "active":
        active_budgets = [b for b in budgets if b.is_active and b.start_date <= today <= b.end_date]
        return render_template("budgets/index.html", budgets=budgets, active_budgets=active_budgets,
                               search_query=search_query, status_filter=status_filter)
    elif status_filter == "future":
        future_budgets = [b for b in budgets if b.is_active and b.start_date > today]
        return render_template("budgets/index.html", budgets=future_budgets, active_budgets=[],
                               search_query=search_query, status_filter=status_filter)
    elif status_filter == "inactive":
        inactive = [b for b in budgets if not b.is_active]
        return render_template("budgets/index.html", budgets=inactive, active_budgets=[],
                               search_query=search_query, status_filter=status_filter)
    else:
        active_budgets = [b for b in budgets if b.is_active and b.start_date <= today <= b.end_date]
        return render_template("budgets/index.html", budgets=budgets, active_budgets=active_budgets,
                               search_query=search_query, status_filter=status_filter)


@budgets_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = BudgetForm()
    categories = Category.query.filter_by(user_id=current_user.id, category_type="expense").all()
    form.category_id.choices = [(0, "-- General --")] + [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        budget = Budget(
            user_id=current_user.id,
            name=form.name.data.strip(),
            category_id=form.category_id.data if form.category_id.data else None,
            amount=round(form.amount.data, 2),
            period=form.period.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
        )
        db.session.add(budget)
        db.session.commit()
        flash("Presupuesto creado.", "success")
        return redirect(url_for("budgets.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("budgets/add.html", form=form)


@budgets_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=budget)
    categories = Category.query.filter_by(user_id=current_user.id, category_type="expense").all()
    form.category_id.choices = [(0, "-- General --")] + [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        budget.name = form.name.data.strip()
        budget.category_id = form.category_id.data if form.category_id.data else None
        budget.amount = round(form.amount.data, 2)
        budget.period = form.period.data
        budget.start_date = form.start_date.data
        budget.end_date = form.end_date.data
        db.session.commit()
        flash("Presupuesto actualizado.", "success")
        return redirect(url_for("budgets.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")
    return render_template("budgets/edit.html", form=form, budget=budget)


@budgets_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    budget.is_active = False
    db.session.commit()
    flash("Presupuesto eliminado.", "info")
    return redirect(url_for("budgets.index"))
