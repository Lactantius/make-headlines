"""News sentiment tracker"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# from flask_migrate import Migrate
# from . import routes, models

# Globally accessible libraries
db = SQLAlchemy()


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    # app.config.from_object("config.Config")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://test:test@0.0.0.0:5401/test"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET")

    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Include our Routes
        from . import routes

        # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)

        # Migration
        # migrate = Migrate(app, db)

        # No need for this
        # Should be taken care of by migrate
        # Create tables for our models
        db.create_all()

        return app
