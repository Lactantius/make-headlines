"""Test Views"""

from flask import request, session
from flask.testing import FlaskClient
from server import create_app
from server.models import Headline, Rewrite, User
import pytest

from .fixtures import set_config_variables, seed_database


def test_index(client: FlaskClient, user: User):
    """Can a user view the index?"""

    with client:

        res = client.get("/")

        assert res.status_code == 200


def test_login_page(client: FlaskClient) -> None:
    """Can a user view the login page?"""
    with client:
        res = client.get("/login")
        assert res.status_code == 200
        assert b'form id="login-form"' in res.data


def test_login(client: FlaskClient) -> None:
    """Can a user login?"""
    with client:
        res = client.post(
            "/login",
            data={
                "username": "test_user",
                "password": "PASSWORD",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Welcome back" in res.data


def test_signup_page(client: FlaskClient) -> None:
    """Can a user view the signup page?"""

    with client:
        res = client.get("/signup")
        assert res.status_code == 200
        assert b'form id="signup-form"' in res.data


def test_signup(client: FlaskClient) -> None:
    """Can a user signup?"""

    with client:
        res = client.post(
            "/signup",
            data={
                "username": "test_signup",
                "email": "test@signup.com",
                "password": "PASSWORD",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Thanks for signing up" in res.data


def test_logout(client: FlaskClient, user: User) -> None:
    """Can a user logout?"""

    with client:
        res = client.post("/logout", follow_redirects=True)

        assert res.status_code == 200
        assert b"Logged out successfully" in res.data
        assert "user_id" not in session


@pytest.fixture
def client(set_config_variables) -> FlaskClient:

    return set_config_variables.test_client()


@pytest.fixture
def user(client) -> User:
    """Add user to session and return"""

    user = User.query.filter(User.username == "test_user").one()
    with client.session_transaction() as session:
        session["user_id"] = user.id

    return user
