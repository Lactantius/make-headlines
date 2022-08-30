"""News sentiment tracker"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Globally accessible libraries
db = SQLAlchemy()


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql:///headlines_test",  # "postgresql+psycopg2://test:test@0.0.0.0:5401/test"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET")

    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Include our Routes
        from . import routes

        db.create_all()

        return app
