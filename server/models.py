"""User and Headline models"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref
import uuid
from flask_bcrypt import Bcrypt
from datetime import date, datetime

from server.analysis import calc_sentiment_score

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)


##############################################################################
# User
#


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    hashed_pwd = db.Column(db.String, nullable=False)


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

    source_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("sources.id"), nullable=False
    )

    source = db.relationship(
        "Source", backref=backref("headlines", cascade="all, delete")
    )


def new_headline(text: str, date: date, source_id: UUID) -> Headline:
    """
    Make new headline object
    Does not store headline in database
    """

    score = calc_sentiment_score(text)

    return Headline(text=text, date=date, source_id=source_id, sentiment_score=score)


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

    semantic_match = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref=backref("rewrites", cascade="all, delete"))

    headline = db.relationship(
        "Headline", backref=backref("rewrites", cascade="all, delete")
    )


def new_rewrite(text: str, headline: Headline, user_id: UUID) -> Rewrite:
    """Build new rewrite. Does not save to database"""

    sentiment_score = calc_sentiment_score(text)
    semantic_match = calc_semantic_match(text, headline.text)

    return Rewrite(
        text=text,
        sentiment_score=sentiment_score,
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
