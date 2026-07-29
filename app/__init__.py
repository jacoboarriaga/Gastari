from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor inicia sesion para acceder."
login_manager.login_message_category = "info"


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.routes import (
        auth_bp,
        dashboard_bp,
        accounts_bp,
        transactions_bp,
        reports_bp,
        debts_bp,
        budgets_bp,
        settings_bp,
        api_bp,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp, url_prefix="/accounts")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(debts_bp, url_prefix="/debts")
    app.register_blueprint(budgets_bp, url_prefix="/budgets")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
