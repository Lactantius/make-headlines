from flask import Flask

import os
from unittest import TestCase
from flask.testing import FlaskClient
from sqlalchemy.exc import IntegrityError
import pytest

from server.models import db, User, Headline, Source, Rewrite, new_user
from server.app import app


#############################################
# User model tests
#


def test_new_user(add_user: User, client: FlaskClient):
    """Can a user be created?"""

    u = add_user
    assert u.username == "test_user"
    assert u.hashed_pwd != "PASSWORD"


#############################################
# Fixtures
#


@pytest.fixture
def client() -> FlaskClient:
    # os.environ["DATABASE_URL"] = "postgresql:///warbler_test"

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///headlines_test"

    app.config["TESTING"] = True
    app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
    app.config["WTF_CSRF_ENABLED"] = False

    # Create our tables (we do this here, so we only create the tables
    # once for all tests --- in each test, we'll delete the data
    # and create fresh new clean test data
    db.create_all()
    return app.test_client()


@pytest.fixture
def add_user() -> User:
    """Add a user and store in database"""

    user = new_user(username="test_user", email="test@test.com", pwd="PASSWORD")
    db.session.add(user)
    db.session.commit()
    return user
