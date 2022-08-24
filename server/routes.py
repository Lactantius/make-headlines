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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

from server.seed import add_headlines
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

# Move this elsewhere
scheduler = BackgroundScheduler()
scheduler.add_job(func=add_headlines, trigger="interval", hours=3)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

##############################################################################
# Decorators
#


def rate_limit(route):
    """Decorator to require a user login before a route"""

    @wraps(route)
    def wrapper(*args, **kwargs):

        current_user = Failure(session.get("user_id")).bind(User.query.get)
        if not current_user.value:

            # This allows the system to have a unique user ID for every rewrite in the system, and to
            # potentially replace the anon user with a real user after login
            anon_user = new_anon_user()
            committed_anon = safe_commit(anon_user)

            session["requests_remaining"] = 2
            session["user_id"] = committed_anon[1].id
            return route(*args, **kwargs, current_user=committed_anon[1].id)

        if current_user.value.anonymous:
            requests_remaining = session.get("requests_remaining", 0)
            if requests_remaining > 0:
                session["requests_remaining"] = requests_remaining - 1
                return route(*args, **kwargs, current_user=current_user.value.id)
            else:
                return (
                    jsonify(error="Please login before making additional requests."),
                    401,
                )

        else:
            return route(*args, **kwargs, current_user=current_user.value.id)

    return wrapper


def get_user(route):
    """Get user from session and pass to route"""

    @wraps(route)
    def wrapper(*args, **kwargs):

        user = Failure(session.get("user_id")).bind(User.query.get)
        return route(*args, **kwargs, current_user=user.value)

    return wrapper


##############################################################################
# JSON API
#


@app.post("/api/rewrites")
@rate_limit
def submit_rewrite(current_user: UUID) -> tuple[Response, int]:
    """Submit headline rewrite"""

    text = request.json.get("text")
    headline_id = request.json.get("headline_id")
    if not text or not headline_id:
        return (jsonify(error="Malformed json request."), 400)

    headline = Failure(headline_id).bind(Headline.query.get)
    if not headline.value:
        return (jsonify(error="Headline not found."), 404)

    rewrite = new_rewrite(text=text, headline=headline.value, user_id=current_user)
    committed_rewrite = safe_commit(rewrite)
    if committed_rewrite[0] == "failure":
        return (jsonify(error="Error saving to database."), 500)

    return (jsonify(rewrite=serialize(committed_rewrite[1])), 201)


@app.get("/api/headlines/random")
def get_random_headline() -> tuple[Response, int]:
    """Get a random headline"""

    # From https://stackoverflow.com/a/33583008/6632828
    headline = Headline.query.order_by(func.random()).first()
    return (jsonify(headline=serialize(headline)), 200)


@app.get("/api/users/<uuid:user_id>/rewrites")
@get_user
def get_all_rewrites(user_id, current_user):
    """
    Get all rewrites by a user
    TODO This is probably much more inefficient than it could be
    """
    if current_user.id != user_id:
        return (jsonify(error="You do not have access to this resource."), 403)

    rewrites = Rewrite.query.filter(Rewrite.user == current_user).all()
    headlines = set([rewrite.headline for rewrite in rewrites])
    json_headlines = [
        serialize(headline, with_rewrites=True, user=current_user)
        for headline in headlines
    ]

    return json_headlines


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
    if session.get("user_id"):
        session.pop("user_id")

    flash("Logged out successfully", "success")
    return redirect("/")


@app.get("/rewrites")
@get_user
def all_rewrites(current_user):

    return render_template("all_rewrites.html", user=current_user)
