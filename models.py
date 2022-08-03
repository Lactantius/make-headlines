"""User and Headline models"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

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

    alignment = db.Column(db.String)
