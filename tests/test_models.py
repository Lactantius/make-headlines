from datetime import date
from uuid import uuid4
from flask import Flask

import os
from flask.testing import FlaskClient
from sqlalchemy.exc import IntegrityError
import pytest

from server.models import (
    db,
    User,
    Headline,
    Source,
    Rewrite,
    new_rewrite,
    new_user,
    new_headline,
    authenticate_user,
)
from server import create_app
from .fixtures import set_config_variables, seed_database

##############################################################################
# User model tests
#


def test_new_user(client: FlaskClient, add_user: User) -> None:
    """Can a user be created?"""

    u = add_user
    assert u.username == "new_user"
    assert u.hashed_pwd != "PASSWORD"
    assert u.id != None
    assert User.query.count() == 2

    etiam = new_user(username="test2", email="email@email.com", pwd="something")
    assert etiam.hashed_pwd != "something"


def test_authenticate_user(client: FlaskClient) -> None:
    """Can a user be authenticated?"""

    user = authenticate_user("test_user", "PASSWORD")
    assert user.username == "test_user"

    bad_password = authenticate_user("test_user", "BAD_PASSWORD")
    assert bad_password == None

    no_user = authenticate_user("bad_username", "PASSWORD")
    assert no_user == None


##############################################################################
# Headline model tests
#


def test_new_headline(client: FlaskClient, add_headline: Headline) -> None:
    """Can a headline be created?"""

    h = add_headline
    assert h.text == "A terrible thing happened"
    assert h.sentiment_score >= -1.0 and h.sentiment_score < 0
    assert h.source.name == "Amazing News"
    assert Headline.query.count() == 2


##############################################################################
# Rewrite model tests
#


def test_new_rewrite(add_rewrite: Rewrite) -> None:
    """Can a rewrite be added?"""

    r = add_rewrite
    assert r.text == "A good thing happened"
    assert r.semantic_match == 1.0
    assert r.sentiment_score <= 1.0 and r.sentiment_score > 0
    assert r.user.username == "test_user"
    assert r.headline.text == "A great thing happened"
    assert Rewrite.query.count() == 2


##############################################################################
# Fixtures
#


@pytest.fixture
def client() -> FlaskClient:

    return create_app().test_client()


@pytest.fixture
def add_user() -> User:
    """Add a user and store in database"""

    user = new_user(username="new_user", email="test@test.com", pwd="PASSWORD")
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
    """Add a headline and store in database"""

    source = Source.query.filter(Source.name == "Amazing News").one()
    headline = new_headline(
        text="A terrible thing happened", date=date.today(), source_id=source.id
    )
    db.session.add(headline)
    db.session.commit()
    return headline


@pytest.fixture
def add_rewrite() -> Rewrite:
    """Add a rewrite and store in database"""

    user = User.query.filter(User.username == "test_user").one()
    headline = Headline.query.filter(Headline.text == "A great thing happened").one()

    rewrite = new_rewrite(
        text="A good thing happened", headline=headline, user_id=user.id
    )
    db.session.add(rewrite)
    db.session.commit()
    return rewrite
