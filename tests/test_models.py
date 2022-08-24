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
    serialize,
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
    assert Headline.query.count() == 3


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
    assert len(r.headline.rewrites) > 0
    assert Rewrite.query.count() == 3


##############################################################################
# Serialize
#


def test_serialize_headline() -> None:
    """
    Are rewrites serialized properly?
    TODO Clean this up to not have three full rewrites.
    """

    headline = Headline.query.filter(Headline.text == "A great thing happened").one()
    user = User.query.filter(User.username == "test_user").one()
    serialized_headline = serialize(headline, with_rewrites=True, user=user)
    cleaned_headline = clean_headline(serialized_headline)
    assert cleaned_headline == {
        "id": 999,
        "source": "Amazing News",
        "source_id": 999,
        "url": "",
        "date": date.today(),
        "text": "A great thing happened",
        "sentiment_score": 0.990334689617157,
        "rewrites": [
            {
                "id": 999,
                "headline_id": 999,
                "semantic_match": 1.0,
                "sentiment_match": -1.6764936447143555,
                "sentiment_score": -0.6861589550971985,
                "text": "An ok thing happened",
                "user_id": 999,
                "timestamp": date.today(),
            },
            {
                "id": 999,
                "headline_id": 999,
                "semantic_match": 1.0,
                "sentiment_match": -0.023634910583496094,
                "sentiment_score": 0.9666997790336609,
                "text": "An interesting thing happened",
                "user_id": 999,
                "timestamp": date.today(),
            },
            {
                "id": 999,
                "headline_id": 999,
                "semantic_match": 1.0,
                "sentiment_match": -0.0008274316787719727,
                "sentiment_score": 0.989507257938385,
                "text": "A good thing happened",
                "user_id": 999,
                "timestamp": date.today(),
            },
        ],
    }


def test_serialize_with_other_user() -> None:
    """Are rewrites serialized properly?"""

    headline = Headline.query.filter(Headline.text == "A great thing happened").one()
    user = User.query.filter(User.username == "new_user").one()
    serialized_headline = serialize(headline, with_rewrites=True, user=user)
    cleaned_headline = clean_headline(serialized_headline)
    assert cleaned_headline == {
        "id": 999,
        "source": "Amazing News",
        "source_id": 999,
        "url": "",
        "date": date.today(),
        "text": "A great thing happened",
        "sentiment_score": 0.990334689617157,
        "rewrites": [],
    }


##############################################################################
# Fixtures and helpers
#
def clean_headline(headline: dict):
    """Make all non-deterministic values deterministic"""

    cleaned = headline.copy()
    cleaned["id"] = 999
    cleaned["source_id"] = 999
    for rewrite in cleaned["rewrites"]:
        rewrite["id"] = 999
        rewrite["headline_id"] = 999
        rewrite["timestamp"] = date.today()
        rewrite["user_id"] = 999
    # if cleaned["rewrites"]:
    #     cleaned["rewrites"] = cleaned["rewrites"][0]

    return cleaned


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
