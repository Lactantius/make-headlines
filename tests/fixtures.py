"""Reused fixtures"""

import pytest
from server import create_app, db
from datetime import date
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient
from server.models import (
    User,
    Rewrite,
    Source,
    Headline,
    # db,
    new_user,
    new_headline,
    new_rewrite,
)


@pytest.fixture(scope="session", autouse=True)
def set_config_variables() -> Flask:
    """Set the config variables and return the app"""
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///headlines_test"

    app.config["TESTING"] = True
    app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
    app.config["WTF_CSRF_ENABLED"] = False

    return app


@pytest.fixture
def client(set_config_variables) -> FlaskClient:
    """Get client"""

    return set_config_variables.test_client()


@pytest.fixture
def user(client) -> User:
    """Add user to session and return"""

    user = User.query.filter(User.username == "test_user").one()
    with client.session_transaction() as session:
        session["user_id"] = user.id

    return user


@pytest.fixture(autouse=True)
def rollback_db() -> None:
    db.session.rollback()


@pytest.fixture(scope="module", autouse=True)
def seed_database(set_config_variables) -> None:

    # create_app().app_context().push()
    set_config_variables.app_context().push()

    db.session.rollback()
    db.drop_all()
    db.create_all()

    user = new_user(username="test_user", email="seed@seed.com", pwd="PASSWORD")
    source = Source(name="Amazing News", alignment="idealist")
    db.session.add_all([user, source])
    db.session.commit()

    headline1 = new_headline(
        text="A great thing happened", date=date.today(), source_id=source.id
    )
    headline2 = new_headline(
        text="Another thing happened", date=date.today(), source_id=source.id
    )
    db.session.add_all([headline1, headline2])
    db.session.commit()

    rewrite1 = new_rewrite(
        text="An ok thing happened", headline=headline1, user_id=user.id
    )
    rewrite2 = new_rewrite(
        text="An interesting thing happened", headline=headline1, user_id=user.id
    )
    db.session.add_all([rewrite1, rewrite2])
    db.session.commit()
