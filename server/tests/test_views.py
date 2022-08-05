"""Test Views"""

from flask.testing import FlaskClient
from server.app import app
from server.models import Headline, Rewrite, User
import pytest


def test_index(client, user):
    """Are expected elements on index?"""

    with client:

        res = client.get("/")

        assert res.status_code == 200


@pytest.fixture
def client() -> FlaskClient:

    return app.test_client()


@pytest.fixture
def user(client) -> User:
    """Add user to session and return"""

    user = User.query.filter(User.username == "test_user").one()
    with client.session_transaction() as session:
        session["user_id"] = user.id

    return user
