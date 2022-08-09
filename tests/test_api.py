"""Test API endpoints"""

from flask.testing import FlaskClient
from server.app import app
from server.models import Headline, Rewrite, User
import pytest

from fixtures import seed_database, set_config_variables

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
            json={"text": "Something definitely happened", "headline_id": headline.id},
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


##############################################################################
# Headlines endpoint
#


def test_get_random_headline(client):
    """Can a random headline be pulled?"""

    with client:
        res = client.get("/api/headlines/random")

        assert res.status_code == 200
        assert res.json["headline"]["text"] != None


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
