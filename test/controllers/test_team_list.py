import json
import uuid

from flask_jwt_extended import create_access_token
from flask_restful import marshal
import pytest

from src.marshallers import TeamMarshaller

pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_team_list_get_without_auth(client):
    """
    WHEN a get request is made to `/teams` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get("/teams")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_team_list_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/teams` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is malformed
    """

    response = client.get("/teams", headers=dict(authorization="abcdefg"))
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_team_list_get_success(client, team1):
    """
    GIVEN there are existing teams on the platform
    WHEN a get request is made to `/teams` with valid authorization
    THEN the response should have a 200 status code and return a list of all users on the platform
    """

    response = client.get(
        "/teams",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 200
    assert json.loads(response.data.decode()) == {
        "data": [dict(marshal(team1, TeamMarshaller.all()))]
    }
