from flask import Blueprint

auth_bp = Blueprint("auth", __name__)
dashboard_bp = Blueprint("dashboard", __name__)
accounts_bp = Blueprint("accounts", __name__)
transactions_bp = Blueprint("transactions", __name__)
reports_bp = Blueprint("reports", __name__)
debts_bp = Blueprint("debts", __name__)
budgets_bp = Blueprint("budgets", __name__)
settings_bp = Blueprint("settings", __name__)
api_bp = Blueprint("api", __name__)

from app.routes import auth_views  # noqa
from app.routes import dashboard_views  # noqa
from app.routes import accounts_views  # noqa
from app.routes import transactions_views  # noqa
from app.routes import reports_views  # noqa
from app.routes import debts_views  # noqa
from app.routes import budgets_views  # noqa
from app.routes import settings_views  # noqa
from app.routes import api_views  # noqa
