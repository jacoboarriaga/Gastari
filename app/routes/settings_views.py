from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import UserSettings, Account
from app.forms import SettingsForm
from app.routes import settings_bp


def get_settings(user):
    settings = UserSettings.query.filter_by(user_id=user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
    return settings


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    settings = get_settings(current_user)
    form = SettingsForm(obj=settings)

    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    form.paycheck_account_id.choices = [(0, "-- Ninguna --")] + [(a.id, a.name) for a in accounts]

    if form.validate_on_submit():
        CURRENCY_SYMBOLS = {
            "MXN": "$", "USD": "$", "EUR": "€", "GBP": "£",
            "GTQ": "Q", "COP": "$", "ARS": "$", "CLP": "$",
            "PEN": "S/", "BRL": "R$",
        }
        settings.currency = form.currency.data
        settings.currency_symbol = CURRENCY_SYMBOLS.get(form.currency.data, "$")
        settings.theme = form.theme.data
        settings.date_format = form.date_format.data
        settings.show_cents = form.show_cents.data
        settings.primary_payment_method = form.primary_payment_method.data
        settings.paycheck_account_id = form.paycheck_account_id.data if form.paycheck_account_id.data else None
        settings.notify_budget_alerts = form.notify_budget_alerts.data
        settings.notify_debt_reminders = form.notify_debt_reminders.data
        settings.monthly_budget_alert_pct = form.monthly_budget_alert_pct.data or 80
        db.session.commit()

        flash("Configuracion guardada.", "success")
        return redirect(url_for("settings.index"))
    elif form.is_submitted():
        flash("Revisa los campos del formulario.", "danger")

    return render_template("settings/index.html", form=form, settings=settings)
