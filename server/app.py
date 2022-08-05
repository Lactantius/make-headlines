"""News sentiment tracker"""

from flask import Flask, redirect, render_template, request, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import DatabaseError, IntegrityError
import os

from server.models import (
    db,
    connect_db,
    User,
    Headline,
    Source,
    Rewrite,
    new_rewrite,
    serialize_rewrite,
)

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


@app.post("/api/rewrites")
def submit_rewrite():
    """Submit headline rewrite"""

    try:
        current_user = User.query.get(session["user_id"])
    except KeyError:
        return (jsonify(error="You must be logged in."), 401)

    try:
        text = request.json["text"]
        headline_id = request.json["headline_id"]
    except KeyError:
        return (jsonify(error="Malformed json request."), 400)

    try:
        headline = Headline.query.get(headline_id)
    except DatabaseError:
        return (jsonify(error="Headline not found."), 404)

    rewrite = new_rewrite(text=text, headline=headline, user_id=current_user.id)
    db.session.add(rewrite)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (jsonify(error="Error saving to database."), 500)

    return (jsonify(rewrite=serialize_rewrite(rewrite)), 201)
