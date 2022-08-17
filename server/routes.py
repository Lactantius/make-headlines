"""Routes"""

from functools import wraps
from uuid import uuid4
from flask import (
    current_app as app,
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    jsonify,
    session,
    Blueprint,
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.sql import func

from server.forms import RewriteForm, SignupForm, LoginForm

from server.models import (
    authenticate_user,
    # db,
    User,
    Headline,
    Source,
    Rewrite,
    new_anon_user,
    new_rewrite,
    new_user,
    serialize,
    Failure,
    safe_commit,
)
from . import db


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


def get_user(route):
    """Get user from session and pass to route"""

    @wraps(route)
    def wrapper(*args, **kwargs):
        try:
            user = User.query.get(session["user_id"])
        except (KeyError, DatabaseError):
            return route(*args, **kwargs, current_user=None)

        return route(*args, **kwargs, current_user=user)

    return wrapper


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
    committed_rewrite = safe_commit(rewrite)
    if committed_rewrite[0] == "failure":
        return (jsonify(error="Error saving to database."), 500)
    # db.session.add(rewrite)

    # try:
    #     db.session.commit()
    # except IntegrityError:
    #     db.session.rollback()
    #     return (jsonify(error="Error saving to database."), 500)

    return (jsonify(rewrite=serialize(committed_rewrite[1])), 201)


@app.get("/api/headlines/random")
def get_random_headline() -> tuple[Response, int]:
    """Get a random headline"""

    # From https://stackoverflow.com/a/33583008/6632828
    headline = Headline.query.order_by(func.random()).first()
    return (jsonify(headline=serialize(headline)), 200)


@app.get("/api/users/<user_id>/rewrites")
@get_user
def get_all_rewrites(user_id, current_user):
    """Get all rewrites by a user"""
    # rewrites = (
    #     db.session.query(Rewrite, Headline)
    #     .filter(Rewrite.user == current_user)
    #     .order_by(Rewrite.headline)
    #     .all()
    # )
    # rewrites = Rewrite.query.filter(Rewrite.user == current_user).all()
    rewrites = Rewrite.query.filter(Rewrite.user == current_user).all()
    headlines = set([rewrite.headline for rewrite in rewrites])
    json_headlines = [
        serialize(headline, with_rewrites=True, user=current_user)
        for headline in headlines
    ]

    # json_rewrites = [serialize(rewrite) for rewrite in rewrites]
    return json_headlines
    # return jsonify(rewrites)
    # if user_id == user.id or user.admin:
    #     rewrites = Rewrite.query.filter(Rewrite.user == user).order_by(Headline.date)
    #     return jsonify()
    # return (
    #     jsonify(error="You must log in to view this information."),
    #     401,
    # )


##############################################################################
# HTML Routes
#


@app.get("/")
@get_user
def index(current_user=None):
    """Get index page"""

    form = RewriteForm()

    return render_template("index.html", form=form, user=current_user)


@app.get("/about")
@get_user
def about(current_user):
    """Get about page"""

    return render_template("about.html", user=current_user)


@app.route("/signup", methods=["GET", "POST"])
@get_user
def signup_page(current_user):
    """Sign up user"""

    if current_user and not current_user.anonymous:
        flash("You are already logged in.", "danger")
        return redirect("/")

    form = SignupForm()
    if form.validate_on_submit():

        user = new_user(
            username=form.username.data, email=form.email.data, pwd=form.password.data
        )
        committed_user = safe_commit(user)
        if committed_user[0] == "failure":
            flash("That username or email is already in use.", "danger")
            return redirect("/signup")

        session["user_id"] = committed_user[1].id
        flash("Thanks for signing up.", "success")
        return redirect("/")

    return render_template("signup.html", form=form, user=current_user)


@app.route("/login", methods=["GET", "POST"])
@get_user
def login_page(current_user):
    """Login user"""

    if current_user and not current_user.anonymous:
        flash("You are already logged in.", "danger")
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.username.data, form.password.data)

        if user:
            session["user_id"] = user.id
            flash(f"Welcome back, {user.username}.", "success")
            return redirect("/")

        else:
            flash("Invalid username or password.", "danger")
            return redirect("/login")

    return render_template("login.html", form=form, user=current_user)


@app.post("/logout")
def logout():
    """Logout user and redirect to index"""
    try:
        session.pop("user_id")
    except KeyError:
        return redirect("/")

    flash("Logged out successfully", "success")
    return redirect("/")
