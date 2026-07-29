from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, TextAreaField, DateField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional
from email_validator import validate_email


DAYS = [(i, str(i)) for i in range(1, 32)]


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasena", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasena", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirmar Contrasena", validators=[DataRequired(), EqualTo("password", message="Las contrasenas no coinciden")]
    )


class AccountForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=1, max=100)])
    account_type = SelectField(
        "Tipo",
        choices=[
            ("checking", "Cuenta de Cheques"),
            ("savings", "Ahorro"),
            ("credit_card", "Tarjeta de Credito"),
            ("cash", "Efectivo"),
            ("investment", "Inversion"),
            ("digital_wallet", "Billetera Digital"),
        ],
        validators=[DataRequired()],
    )
    balance = FloatField("Saldo/Deuda", default=0.0)
    currency = SelectField("Moneda", choices=[("MXN", "MXN"), ("USD", "USD"), ("EUR", "EUR")], default="MXN")
    color = StringField("Color", default="#10B981")
    icon = StringField("Icono", default="wallet")
    credit_limit = FloatField("Limite de credito", validators=[Optional()])
    closing_day = SelectField("Dia de cierre", coerce=int, choices=[(0, "-- Ninguno --")] + DAYS, validators=[Optional()])
    payment_day = SelectField("Dia de pago", coerce=int, choices=[(0, "-- Ninguno --")] + DAYS, validators=[Optional()])
    interest_rate = FloatField("Tasa de interes (%)", validators=[Optional(), NumberRange(min=0, max=200)])


class TransactionForm(FlaskForm):
    account_id = SelectField("Cuenta", coerce=int, validators=[DataRequired()])
    transaction_type = SelectField(
        "Tipo",
        choices=[
            ("income", "Ingreso"),
            ("expense", "Gasto"),
            ("transfer", "Transferencia"),
        ],
        validators=[DataRequired()],
    )
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0.01)])
    category_id = SelectField("Categoria", coerce=int, validators=[Optional()])
    to_account_id = SelectField("Cuenta destino", coerce=int, validators=[Optional()])
    description = StringField("Descripcion", validators=[Optional(), Length(max=200)])
    date = DateField("Fecha", validators=[DataRequired()])
    notes = TextAreaField("Notas", validators=[Optional()])
    is_recurring = BooleanField("Recurrente", default=False)
    recurring_frequency = SelectField(
        "Frecuencia",
        choices=[
            ("", "Ninguna"),
            ("daily", "Diario"),
            ("weekly", "Semanal"),
            ("biweekly", "Quincenal"),
            ("monthly", "Mensual"),
            ("yearly", "Anual"),
        ],
        validators=[Optional()],
    )


class CategoryForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=1, max=50)])
    category_type = SelectField(
        "Tipo", choices=[("income", "Ingreso"), ("expense", "Gasto")], validators=[DataRequired()]
    )
    icon = StringField("Icono", default="tag")
    color = StringField("Color", default="#6366F1")


class DebtForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=1, max=100)])
    debt_type = SelectField(
        "Tipo",
        choices=[
            ("credit_card", "Tarjeta de Credito"),
            ("personal_loan", "Prestamo Personal"),
            ("mortgage", "Hipoteca"),
            ("auto_loan", "Prestamo Auto"),
            ("student_loan", "Prestamo Estudiantil"),
            ("other", "Otro"),
        ],
        validators=[DataRequired()],
    )
    original_amount = FloatField("Monto original", validators=[DataRequired(), NumberRange(min=0.01)])
    current_amount = FloatField("Monto actual", validators=[DataRequired(), NumberRange(min=0)])
    interest_rate = FloatField("Tasa de interes (%)", default=0.0, validators=[NumberRange(min=0, max=200)])
    minimum_payment = FloatField("Pago minimo", validators=[Optional()])
    due_day = SelectField("Dia de vencimiento", coerce=int, choices=[(0, "-- Ninguno --")] + DAYS, validators=[Optional()])
    creditor = StringField("Acreedor", validators=[Optional(), Length(max=100)])
    start_date = DateField("Fecha inicio", validators=[Optional()])
    end_date = DateField("Fecha fin", validators=[Optional()])


class BudgetForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=1, max=100)])
    category_id = SelectField("Categoria", coerce=int, validators=[Optional()])
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0.01)])
    period = SelectField(
        "Periodo",
        choices=[("weekly", "Semanal"), ("biweekly", "Quincenal"), ("monthly", "Mensual"), ("yearly", "Anual")],
        default="monthly",
    )
    start_date = DateField("Fecha inicio", validators=[DataRequired()])
    end_date = DateField("Fecha fin", validators=[DataRequired()])


class GoalForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=1, max=100)])
    target_amount = FloatField("Monto meta", validators=[DataRequired(), NumberRange(min=0.01)])
    current_amount = FloatField("Monto actual", default=0.0)
    target_date = DateField("Fecha meta", validators=[Optional()])
    color = StringField("Color", default="#F59E0B")


class SettingsForm(FlaskForm):
    currency = SelectField(
        "Moneda",
        choices=[
            ("MXN", "MXN - Peso Mexicano"),
            ("USD", "USD - Dolar Americano"),
            ("EUR", "EUR - Euro"),
            ("GBP", "GBP - Libra Esterlina"),
            ("GTQ", "GTQ - Quetzal"),
            ("COP", "COP - Peso Colombiano"),
            ("ARS", "ARS - Peso Argentino"),
            ("CLP", "CLP - Peso Chileno"),
            ("PEN", "PEN - Sol Peruano"),
            ("BRL", "BRL - Real"),
        ],
        validators=[DataRequired()],
    )
    theme = SelectField(
        "Tema",
        choices=[("light", "Claro"), ("dark", "Oscuro"), ("system", "Automatico (Sistema)")],
        default="light",
    )
    date_format = SelectField(
        "Formato de fecha",
        choices=[("DD/MM/YYYY", "DD/MM/YYYY"), ("MM/DD/YYYY", "MM/DD/YYYY"), ("YYYY-MM-DD", "YYYY-MM-DD")],
        default="DD/MM/YYYY",
    )
    show_cents = BooleanField("Mostrar centavos", default=False)
    primary_payment_method = SelectField(
        "Metodo de pago principal",
        choices=[
            ("cash", "Efectivo"),
            ("debit", "Tarjeta de debito"),
            ("credit", "Tarjeta de credito"),
            ("transfer", "Transferencia"),
            ("digital", "Billetera digital"),
        ],
        default="debit",
    )
    paycheck_account_id = SelectField("Cuenta de recibos de nomina", coerce=int, validators=[Optional()])
    notify_budget_alerts = BooleanField("Alertas de presupuesto", default=True)
    notify_debt_reminders = BooleanField("Recordatorios de deudas", default=True)
    monthly_budget_alert_pct = IntegerField(
        "Alertar al % del presupuesto", validators=[Optional(), NumberRange(min=1, max=100)], default=80
    )
