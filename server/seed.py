"""Commands for resetting the database and adding more headlines"""
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from server.models import User, Headline, Rewrite, Source
from server import db, create_app
from server.feeds import send_to_database


def reset_database():
    """Deletes and recreates all tables"""
    db.session.rollback()
    db.drop_all()
    db.create_all()


def add_sources():
    """Add sources to source table"""
    sources = [
        {"name": "New York Times", "url": "nytimes.com", "alignment": "left"},
        {"name": "Wall Street Journal", "url": "wsj.com", "alignment": "right"},
    ]

    for source in sources:
        db.session.add(Source(**source))

    db.session.commit()


def add_headlines():
    """Add headlines to database"""
    with create_app().app_context():
        nytimes = Source.query.filter(Source.name == "New York Times").one()
        wsj = Source.query.filter(Source.name == "Wall Street Journal").one()
        send_to_database(nytimes)
        send_to_database(wsj)


def seed():
    """Seed all"""

    with create_app().app_context():
        reset_database()
        add_sources()
        add_headlines()


if __name__ == "__main__":

    seed()
