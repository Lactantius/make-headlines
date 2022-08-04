from datetime import date
from uuid import uuid4
from flask import Flask

import os
from unittest import TestCase
from flask.testing import FlaskClient
from sqlalchemy.exc import IntegrityError
import pytest

from server.models import db, User, Headline, Source, Rewrite, new_user, new_headline
from server.app import app

##############################################################################
# User model tests
#


def test_new_user(client: FlaskClient, add_user: User) -> None:
    """Can a user be created?"""

    u = add_user
    assert u.username == "test_user"
    assert u.hashed_pwd != "PASSWORD"
    assert u.id != None
    assert User.query.count() == 2

    etiam = new_user(username="test2", email="email@email.com", pwd="something")
    assert etiam.hashed_pwd != "something"


##############################################################################
# Headline model tests
#


def test_new_headline(client: FlaskClient, add_headline: Headline) -> None:
    """Can a headline be created?"""

    h = add_headline
    assert h.text == "A terrible thing happened"
    assert h.score == 1.0
    assert h.source.name == "Amazing News"
    assert Headline.query.count() == 2


##############################################################################
# Fixtures
#


@pytest.fixture(scope="session", autouse=True)
def set_config_variables() -> None:
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///headlines_test"

    app.config["TESTING"] = True
    app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
    app.config["WTF_CSRF_ENABLED"] = False


@pytest.fixture(scope="session", autouse=True)
def seed_database() -> None:

    db.drop_all()
    db.create_all()

    user = new_user(username="seed_user", email="seed@seed.com", pwd="PASSWORD")
    source = Source(name="Amazing News", alignment="idealist")
    db.session.add_all([user, source])
    db.session.commit()

    headline = new_headline(
        text="A great thing happened", date=date.today(), source_id=source.id
    )
    db.session.add(headline)
    db.session.commit()


@pytest.fixture
def client() -> FlaskClient:
    # os.environ["DATABASE_URL"] = "postgresql:///warbler_test"

    # app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///headlines_test"

    # app.config["TESTING"] = True
    # app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
    # app.config["WTF_CSRF_ENABLED"] = False

    # Create our tables (we do this here, so we only create the tables
    # once for all tests --- in each test, we'll delete the data
    # and create fresh new clean test data

    return app.test_client()


@pytest.fixture
def add_user() -> User:
    """Add a user and store in database"""

    user = new_user(username="test_user", email="test@test.com", pwd="PASSWORD")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def add_source() -> Source:
    """Add a source and store in database"""

    source = Source(name="Excellent News", alignment="weird")
    db.session.add(source)
    db.session.commit()
    return source


@pytest.fixture
def add_headline() -> Headline:
    """Add a headline adn store in database"""

    source = Source.query.filter(Source.name == "Amazing News").one()
    headline = new_headline(
        text="A terrible thing happened", date=date.today(), source_id=source.id
    )
    db.session.add(headline)
    db.session.commit()
    return headline
