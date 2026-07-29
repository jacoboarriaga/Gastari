from datetime import datetime, date
from app import db, login_manager
from flask_login import UserMixin
import bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    accounts = db.relationship("Account", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    debts = db.relationship("Debt", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="owner", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def __repr__(self):
        return f"<User {self.email}>"


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default="MXN")
    color = db.Column(db.String(7), default="#10B981")
    icon = db.Column(db.String(50), default="wallet")
    is_active = db.Column(db.Boolean, default=True)
    credit_limit = db.Column(db.Float, nullable=True)
    closing_day = db.Column(db.Integer, nullable=True)
    payment_day = db.Column(db.Integer, nullable=True)
    interest_rate = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="account", lazy="dynamic", cascade="all, delete-orphan", foreign_keys="[Transaction.account_id]")

    @property
    def available_credit(self):
        if self.credit_limit:
            return self.credit_limit + self.balance
        return None

    def __repr__(self):
        return f"<Account {self.name}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    category_type = db.Column(db.String(20), nullable=False)
    icon = db.Column(db.String(50), default="tag")
    color = db.Column(db.String(7), default="#6366F1")
    is_default = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    subcategories = db.relationship("Category", backref=db.backref("parent", remote_side=[id]), lazy="dynamic")
    transactions = db.relationship("Transaction", backref="category", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("user_id", "name", "category_type", name="unique_category_per_user"),)

    def __repr__(self):
        return f"<Category {self.name}>"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    debt_id = db.Column(db.Integer, db.ForeignKey("debts.id"), nullable=True)
    attachment_path = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    to_account = db.relationship("Account", foreign_keys=[to_account_id], backref="transfers_in")

    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.amount}>"


class Debt(db.Model):
    __tablename__ = "debts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    debt_type = db.Column(db.String(30), nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    minimum_payment = db.Column(db.Float, nullable=True)
    due_day = db.Column(db.Integer, nullable=True)
    creditor = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship("Transaction", backref="debt", lazy="dynamic")

    @property
    def progress_percent(self):
        if self.original_amount > 0:
            paid = self.original_amount - self.current_amount
            return round((paid / self.original_amount) * 100, 1)
        return 0

    def __repr__(self):
        return f"<Debt {self.name}>"


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    spent = db.Column(db.Float, default=0.0)
    period = db.Column(db.String(20), default="monthly")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", backref="budgets")

    @property
    def remaining(self):
        return round(self.amount - self.spent, 2)

    @property
    def progress_percent(self):
        if self.amount > 0:
            return round((self.spent / self.amount) * 100, 1)
        return 0

    @property
    def days_left(self):
        today = date.today()
        if today > self.end_date:
            return 0
        if today < self.start_date:
            return (self.end_date - self.start_date).days
        return (self.end_date - today).days

    @property
    def days_total(self):
        return (self.end_date - self.start_date).days or 1

    @property
    def days_elapsed(self):
        today = date.today()
        if today < self.start_date:
            return 0
        if today > self.end_date:
            return self.days_total
        return (today - self.start_date).days

    @property
    def daily_average(self):
        elapsed = self.days_elapsed
        if elapsed <= 0:
            return 0
        return round(self.spent / elapsed, 2)

    @property
    def daily_budget(self):
        return round(self.amount / self.days_total, 2)

    @property
    def projected_total(self):
        elapsed = self.days_elapsed
        if elapsed <= 0:
            return 0
        return round(self.daily_average * self.days_total, 2)

    @property
    def velocity_status(self):
        if self.progress_percent <= 0:
            return "neutral"
        time_pct = (self.days_elapsed / self.days_total * 100) if self.days_total > 0 else 0
        if self.progress_percent > time_pct + 10:
            return "over"
        elif self.progress_percent < time_pct - 10:
            return "under"
        return "on_track"

    @property
    def status_label(self):
        vs = self.velocity_status
        if vs == "over":
            return "Sobre el ritmo"
        elif vs == "under":
            return "Bajo el ritmo"
        return "En camino"

    @property
    def progress_status(self):
        if self.progress_percent > 90:
            return "danger"
        elif self.progress_percent > 70:
            return "warning"
        return "ok"

    def __repr__(self):
        return f"<Budget {self.name}>"


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    icon = db.Column(db.String(50), default="target")
    color = db.Column(db.String(7), default="#F59E0B")
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def progress_percent(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 1)
        return 0

    def __repr__(self):
        return f"<Goal {self.name}>"


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    currency = db.Column(db.String(3), default="MXN")
    currency_symbol = db.Column(db.String(5), default="$")
    theme = db.Column(db.String(10), default="light")
    date_format = db.Column(db.String(20), default="DD/MM/YYYY")
    language = db.Column(db.String(5), default="es")
    show_cents = db.Column(db.Boolean, default=False)

    primary_payment_method = db.Column(db.String(20), default="debit")
    paycheck_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)

    notify_budget_alerts = db.Column(db.Boolean, default=True)
    notify_debt_reminders = db.Column(db.Boolean, default=True)
    monthly_budget_alert_pct = db.Column(db.Integer, default=80)

    user = db.relationship("User", backref=db.backref("settings", uselist=False))
    paycheck_account = db.relationship("Account", foreign_keys=[paycheck_account_id])

    CURRENCIES = {
        "MXN": ("$", "Peso Mexicano"),
        "USD": ("$", "Dolar Americano"),
        "EUR": ("€", "Euro"),
        "GBP": ("£", "Libra Esterlina"),
        "GTQ": ("Q", "Quetzal"),
        "COP": ("$", "Peso Colombiano"),
        "ARS": ("$", "Peso Argentino"),
        "CLP": ("$", "Peso Chileno"),
        "PEN": ("S/", "Sol Peruano"),
        "BRL": ("R$", "Real Brasileño"),
    }

    def format_amount(self, amount):
        if self.show_cents:
            return f"{self.currency_symbol}{amount:,.2f}"
        return f"{self.currency_symbol}{amount:,.0f}"

    def __repr__(self):
        return f"<UserSettings {self.currency}>"
