"""News sentiment tracker"""

from functools import wraps
from uuid import uuid4
from flask import Flask, Response, redirect, render_template, request, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import DatabaseError, IntegrityError
import os
from sqlalchemy.sql import func

from server.models import (
    db,
    connect_db,
    User,
    Headline,
    Source,
    Rewrite,
    new_anon_user,
    new_rewrite,
    serialize,
)

from server.forms import RewriteForm

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

##############################################################################
# Decorators
#


def rate_limit(route):
    """Decorator to require a user login before a route"""

    @wraps(route)
    def wrapper(*args, **kwargs):

        try:
            current_user = User.query.get(session["user_id"])
        except (KeyError, DatabaseError):

            # This allows the system to have a unique user ID for every rewrite in the system, and to
            # potentially replace the anon user with a real user after login
            anon_user = new_anon_user()
            db.session.add(anon_user)
            db.session.commit()

            session["requests_remaining"] = 2
            session["user_id"] = anon_user.id
            return route(*args, **kwargs, current_user=anon_user.id)

        if current_user.anonymous:
            requests_remaining = session.get("requests_remaining", 0)
            if requests_remaining > 0:
                session["requests_remaining"] = requests_remaining - 1
                return route(*args, **kwargs, current_user=current_user.id)
            else:
                return (
                    jsonify(error="Please login before making additional requests."),
                    401,
                )

        else:
            return route(*args, **kwargs, current_user=current_user.id)

    return wrapper
    # match session.get("requests_remaining", None):

    #     case None:
    #         session["requests_remaining"] = 9
    #         return route(*args, **kwargs, current_user=anon_user.id)

    #     case 0:
    #         return (
    #             jsonify(
    #                 error="Please login before making additional requests."
    #             ),
    #             401,
    #         )

    #     case int() as requests_remaining if requests_remaining > 0:
    #         temp_user = session["user_id"]
    #         return route(*args, **kwargs, current_user=temp_user)

    #     case _:
    #         return (
    #             jsonify(
    #                 error="Please login before making additional requests."
    #             ),
    #             401,
    #         )


##############################################################################
# JSON API
#


@app.post("/api/rewrites")
@rate_limit
def submit_rewrite(current_user: UUID) -> tuple[Response, int]:
    """Submit headline rewrite"""

    try:
        text = request.json["text"]
        headline_id = request.json["headline_id"]
    except KeyError:
        return (jsonify(error="Malformed json request."), 400)

    try:
        headline = Headline.query.get(headline_id)
    except DatabaseError:
        return (jsonify(error="Headline not found."), 404)

    rewrite = new_rewrite(text=text, headline=headline, user_id=current_user)
    db.session.add(rewrite)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (jsonify(error="Error saving to database."), 500)

    return (jsonify(rewrite=serialize(rewrite)), 201)


@app.get("/api/headlines/random")
def get_random_headline() -> tuple[Response, int]:
    """Get a random headline"""

    # From https://stackoverflow.com/a/33583008/6632828
    headline = Headline.query.order_by(func.random()).first()
    return (jsonify(headline=serialize(headline)), 200)


##############################################################################
# HTML Routes
#


@app.get("/")
def index():
    """Get index page"""

    form = RewriteForm()

    return render_template("index.html", form=form)
