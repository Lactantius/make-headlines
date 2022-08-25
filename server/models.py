"""User and Headline models"""

from collections.abc import Callable
from typing import Dict
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import backref
import uuid
from flask_bcrypt import Bcrypt
from datetime import date, datetime
import traceback

from server.analysis import calc_sentiment_score

bcrypt = Bcrypt()
from . import db


##############################################################################
# User
#


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = db.Column(db.String(100), nullable=False, unique=True)

    email = db.Column(db.String(100), nullable=False, unique=True)

    hashed_pwd = db.Column(db.String)

    admin = db.Column(db.Boolean, default=False)

    active = db.Column(db.Boolean, default=True)

    anonymous = db.Column(db.Boolean, default=False)


def authenticate_user(username: str, password: str) -> User | None:
    """Get a user from the database given a username/email and password"""

    try:
        user = User.query.filter(
            (User.email == username) | (User.username == username)
        ).one()
    except NoResultFound:
        return None

    if bcrypt.check_password_hash(user.hashed_pwd, password):
        return user
    else:
        return None


##############################################################################
# Headline
#


class Headline(db.Model):
    """Headline"""

    __tablename__ = "headlines"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    text = db.Column(db.String, nullable=False)

    sentiment_score = db.Column(db.Float, nullable=False)

    date = db.Column(db.Date, nullable=False)

    url = db.Column(db.String)

    source_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("sources.id"), nullable=False
    )

    source = db.relationship(
        "Source", backref=backref("headlines", cascade="all, delete")
    )


def new_headline(text: str, date: date, source_id: UUID, url="") -> Headline:
    """
    Make new headline object
    Does not store headline in database
    """

    score = calc_sentiment_score(text)

    return Headline(
        text=text, date=date, source_id=source_id, url=url, sentiment_score=score
    )


# def calc_sentiment_score(text: str) -> float:
#     """TODO Use Flair to actually calculate this."""

#     return 1.0


##############################################################################
# Rewrite
#


class Source(db.Model):
    """News Source"""

    __tablename__ = "sources"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String)

    url = db.Column(db.String)

    # Political alignment
    alignment = db.Column(db.String)


##############################################################################
# Rewrite
#


class Rewrite(db.Model):
    """User headline rewrite"""

    __tablename__ = "rewrites"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    text = db.Column(db.String, nullable=False)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    headline_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("headlines.id"), nullable=False
    )

    sentiment_score = db.Column(db.Float, nullable=False)

    sentiment_match = db.Column(db.Float, nullable=False)

    semantic_match = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref=backref("rewrites", cascade="all, delete"))

    headline = db.relationship(
        "Headline", backref=backref("rewrites", cascade="all, delete")
    )


def new_rewrite(text: str, headline: Headline, user_id: UUID) -> Rewrite:
    """Build new rewrite. Does not save to database"""

    sentiment_score = calc_sentiment_score(text)
    sentiment_match = sentiment_score - headline.sentiment_score
    semantic_match = calc_semantic_match(text, headline.text)

    return Rewrite(
        text=text,
        sentiment_score=sentiment_score,
        sentiment_match=sentiment_match,
        semantic_match=semantic_match,
        user_id=user_id,
        headline_id=headline.id,
    )


def calc_semantic_match(rewrite: str, headline: str) -> float:
    """TODO Use Gensim"""

    return 1.0


###################################################
# Functions
#


def new_user(username: str, email: str, pwd: str) -> User:
    """
    Register user, add attach hashed password, and return user.
    Does not store user in database.
    """

    hashed_pwd = bcrypt.generate_password_hash(pwd)
    hashed_utf8 = hashed_pwd.decode("utf8")

    return User(
        username=username,
        email=email,
        hashed_pwd=hashed_utf8,
    )


def safe_commit(obj: object | None) -> tuple[str, object]:
    # return Failure(obj).bind(db.session.add).bind(db.session.commit)
    if obj:
        db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return ("failure", obj)

    return ("success", obj)


def safe_delete(obj: object) -> str:
    try:
        db.session.delete(obj)
        db.session.commit()
        return "success"
    except IntegrityError:
        db.session.rollback()
        return "failure"


def new_anon_user():
    """
    Register a user with placeholders for username and email, so that rewrites can be stored in the database.
    Does not store user in database
    """

    return User(username=uuid.uuid4(), email=uuid.uuid4(), anonymous=True)


def serialize(
    obj: (Headline | Rewrite), with_rewrites=False, user=None
) -> dict[str, (str | float)]:
    """Return serialized headline"""

    match obj:
        case Headline():
            if with_rewrites:
                if user:
                    return {
                        "id": obj.id,
                        "text": obj.text,
                        "sentiment_score": obj.sentiment_score,
                        "date": obj.date,
                        "source_id": obj.source_id,
                        "source": obj.source.name,
                        "url": obj.url,
                        "rewrites": [
                            serialize(rewrite)
                            for rewrite in obj.rewrites
                            if rewrite.user == user
                        ],
                    }
                return {
                    "id": obj.id,
                    "text": obj.text,
                    "sentiment_score": obj.sentiment_score,
                    "date": obj.date,
                    "source_id": obj.source_id,
                    "source": obj.source.name,
                    "url": obj.url,
                    "rewrites": [serialize(rewrite) for rewrite in obj.rewrites],
                }
            return {
                "id": obj.id,
                "text": obj.text,
                "sentiment_score": obj.sentiment_score,
                "date": obj.date,
                "source_id": obj.source_id,
                "source": obj.source.name,
                "url": obj.url,
            }

        case Rewrite():
            return {
                "id": obj.id,
                "text": obj.text,
                "sentiment_score": obj.sentiment_score,
                "sentiment_match": obj.sentiment_match,
                "semantic_match": obj.semantic_match,
                "user_id": obj.user_id,
                "headline_id": obj.headline_id,
                "timestamp": obj.timestamp,
            }


###################################################
# Monads
#


class Failure:
    """Monad from https://www.philliams.com/monads-in-python"""

    def __init__(self, value: object = None, errors: Dict = None):
        self.value = value
        self.errors = errors

    def bind(self, f: Callable, *args, **kwargs) -> "Failure":

        if self.errors:
            return Failure(None, errors=self.errors)

        try:
            result = f(self.value, *args, **kwargs)
            return Failure(result)
        except Exception as e:

            failure_status = {
                "trace": traceback.format_exc(),
                "exc": e,
                "args": args,
                "kwargs": kwargs,
            }

            return Failure(None, errors=failure_status)
