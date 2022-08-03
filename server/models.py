"""User and Headline models"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_bcrypt import Bcrypt

from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    hashed_pwd = db.Column(db.String, nullable=False)


class Headline(db.Model):
    """Headline"""

    __tablename__ = "headlines"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    text = db.Column(db.String, nullable=False)

    score = db.Column(db.Float, nullable=False)

    date = db.Column(db.Date, nullable=False)

    source_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("sources.id"), nullable=False
    )


class Source(db.Model):
    """News Source"""

    __tablename__ = "sources"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String)

    # Political alignment
    alignment = db.Column(db.String)


class Rewrite(db.Model):
    """User headline rewrite"""

    __tablename__ = "rewrites"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    headline_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("headlines.id"), nullable=False
    )

    sentiment_score = db.Column(db.Float, nullable=False)

    semantic_match = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now())


###################################################
# Functions
#


def new_user(username, email, pwd):
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
