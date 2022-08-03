"""News sentiment tracker"""

from flask import Flask, redirect, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
import os

from models import db, connect_db, User, Headline, Source, Rewrite

# from forms import RewriteForm

app = Flask(__name__)

# From https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
uri = os.environ.get("DATABASE_URL", "postgresql:///headlines_dev")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET")

if os.getenv("FLASK_ENV") == "development":
    from flask_debugtoolbar import DebugToolbarExtension

    toolbar = DebugToolbarExtension(app)
    app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)
db.create_all()
