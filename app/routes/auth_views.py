from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Category
from app.forms import LoginForm, RegisterForm
from app.routes import auth_bp


def create_default_categories(user):
    expense_categories = [
        ("Alimentacion", "utensils", "#EF4444"),
        ("Transporte", "car", "#F97316"),
        ("Vivienda", "home", "#3B82F6"),
        ("Servicios", "zap", "#8B5CF6"),
        ("Salud", "heart-pulse", "#EC4899"),
        ("Educacion", "graduation-cap", "#06B6D4"),
        ("Entretenimiento", "gamepad-2", "#10B981"),
        ("Ropa", "shirt", "#F59E0B"),
        ("Tecnologia", "smartphone", "#6366F1"),
        ("Suscripciones", "repeat", "#A855F7"),
        ("Mascotas", "paw-print", "#14B8A6"),
        ("Hogar", "sofa", "#84CC16"),
        ("Otros Gastos", "tag", "#6B7280"),
        ("Pago de Tarjeta", "credit-card", "#DC2626"),
        ("Retiro de Efectivo", "banknote", "#059669"),
    ]
    income_categories = [
        ("Salario", "briefcase", "#10B981"),
        ("Freelance", "laptop", "#3B82F6"),
        ("Inversiones", "trending-up", "#F59E0B"),
        ("Otros Ingresos", "plus-circle", "#6366F1"),
    ]
    for name, icon, color in expense_categories:
        db.session.add(Category(user_id=user.id, name=name, category_type="expense", icon=icon, color=color, is_default=True))
    for name, icon, color in income_categories:
        db.session.add(Category(user_id=user.id, name=name, category_type="income", icon=icon, color=color, is_default=True))
    db.session.commit()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get("next")
            flash("Bienvenido de nuevo!", "success")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Email o contrasena incorrectos.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("Este email ya esta registrado.", "warning")
            return render_template("auth/register.html", form=form)
        user = User(name=form.name.data.strip(), email=form.email.data.lower().strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        create_default_categories(user)
        login_user(user)
        flash("Cuenta creada correctamente! Bienvenido a Gastari.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Session cerrada.", "info")
    return redirect(url_for("auth.login"))
