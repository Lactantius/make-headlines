#!/usr/bin/env python3

from server.models import User, Headline, Rewrite, Source
from server.app import db
from server.feeds import send_to_database


def reset_database():
    db.session.rollback()
    db.drop_all()
    db.create_all()


def add_sources():
    sources = [
        {"name": "New York Times", "url": "nytimes.com", "alignment": "left"},
        {"name": "Wall Street Journal", "url": "wsj.com", "alignment": "right"},
    ]

    for source in sources:
        db.session.add(Source(**source))

    db.session.commit()


def add_headlines():
    nytimes = Source.query.filter(Source.name == "New York Times").one()
    send_to_database(nytimes)
