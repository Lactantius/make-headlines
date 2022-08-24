"""Test API endpoints"""

from flask import session
from flask.testing import FlaskClient
from server import create_app
from server.models import Headline, Rewrite, User
import pytest

from .fixtures import seed_database, set_config_variables, client, rollback_db, user

##############################################################################
# Rewrites endpoint
#


def test_submit_rewrite(client, user):
    """Can a user submit a rewrite for a headline?"""

    with client:

        headline = Headline.query.filter(
            Headline.text == "A great thing happened"
        ).one()

        res = client.post(
            "/api/rewrites",
            json={
                "text": "Something definitely happened",
                "headline_id": headline.id,
            },
        )

        assert res.status_code == 201
        assert res.json["rewrite"]["text"] == "Something definitely happened"
        # assert Rewrite.query.count() == 3


def test_submit_rewrite_error_handling(client, user):
    """Are malformed post requests to /api/rewrites handled properly?"""

    with client:

        no_headline = client.post(
            "/api/rewrites",
            json={"text": "Something definitely happened"},
        )

        assert no_headline.status_code == 400
        assert no_headline.json == {"error": "Malformed json request."}

        headline_not_in_db = client.post(
            "/api/rewrites",
            json={"text": "Something definitely happened", "headline_id": "invalid_id"},
        )

        assert headline_not_in_db.status_code == 404
        assert headline_not_in_db.json == {"error": "Headline not found."}


def test_unauthenticated_user_handling(client):
    """Can unauthenticated users submit rewrites?"""

    headline = Headline.query.filter(Headline.text == "A great thing happened").one()

    res = client.post(
        "/api/rewrites",
        json={"text": "Something definitely happened", "headline_id": headline.id},
    )

    assert res.status_code == 201
    assert res.json["rewrite"]["text"] == "Something definitely happened"


def test_rate_limit_unauthenticated_users(client):
    """Can unauthenticated users submit unlimited rewrites?"""

    headline_id = (
        Headline.query.filter(Headline.text == "A great thing happened").one().id
    )

    with client:

        for x in range(4):
            no_user = client.post(
                "/api/rewrites",
                json={
                    "text": "Something definitely happened",
                    "headline_id": headline_id,
                },
            )

        assert no_user.status_code == 401
        assert no_user.json == {
            "error": "Please login before making additional requests."
        }


def test_get_all_headlines_for_user(client, user):
    """Can a logged in user get all rewrites?"""

    with client:
        res = client.get(f"/api/users/{user.id}/rewrites")
        assert len(res.json) == 1
        assert len(res.json[0]["rewrites"]) == 3


def test_cannot_get_rewrites_of_other_user(client, user):
    """Will a user be prevented from seeing another user's rewrites?"""

    with client:
        user2 = User.query.filter(User.username == "another_user").one()
        res = client.get(f"/api/users/{user2.id}/rewrites")
        assert res.status_code == 403
        assert res.json == {"error": "You do not have access to this resource."}


##############################################################################
# Headlines endpoint
#


def test_get_random_headline(client):
    """Can a random headline be pulled?"""

    with client:
        res = client.get("/api/headlines/random")

        assert res.status_code == 200
        assert res.json["headline"]["text"] != None


##############################################################################
# Views
#


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
