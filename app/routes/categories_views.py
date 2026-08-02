from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Category
from app.forms import CategoryForm
from app.routes import categories_bp


@categories_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    category_type = request.args.get("type", "")

    query = Category.query.filter_by(user_id=current_user.id)

    if category_type in ("income", "expense"):
        query = query.filter_by(category_type=category_type)

    if q:
        query = query.filter(Category.name.ilike(f"%{q}%"))

    categories = query.order_by(Category.category_type, Category.name).all()

    return render_template(
        "categories/index.html",
        categories=categories,
        search_query=q,
        category_type=category_type,
    )


@categories_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = Category(
            user_id=current_user.id,
            name=form.name.data.strip(),
            category_type=form.category_type.data,
        )
        db.session.add(cat)
        db.session.commit()
        flash("Categoria creada.", "success")
        return redirect(url_for("categories.index"))
    return render_template("categories/add.html", form=form)


@categories_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    cat = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data.strip()
        cat.category_type = form.category_type.data
        db.session.commit()
        flash("Categoria actualizada.", "success")
        return redirect(url_for("categories.index"))
    return render_template("categories/edit.html", form=form, category=cat)


@categories_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    cat = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(cat)
    db.session.commit()
    flash("Categoria eliminada.", "success")
    return redirect(url_for("categories.index"))
