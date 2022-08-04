"""Test API endpoints"""

from flask.testing import FlaskClient
from server.app import app
from server.models import Headline, Rewrite, User


def test_submit_rewrite():
    """Can a user submit a rewrite for a headline?"""

    with app.test_client() as client:

        user = User.query.filter(User.username == "test_user").one()
        headline = Headline.query.filter(
            Headline.text == "A great thing happened"
        ).one()

        with client.session_transaction() as session:
            session["user_id"] = user.id

        res = client.post(
            "/api/rewrites",
            json={"text": "Something definitely happened", "headline_id": headline.id},
        )

        assert res.status_code == 201
        assert res.json["rewrite"]["text"] == "Something definitely happened"
        assert Rewrite.query.count() == 2
