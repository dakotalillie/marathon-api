import json
import uuid

from flask_jwt_extended import create_access_token
from flask_restful import marshal
import pytest

from src.exceptions import BadRequestError, NotFoundError
from src.marshallers import TeamMarshaller

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_team_detail_get_without_auth(client):
    """
    WHEN a get request is made to to `/teams/<team_id>` without a token in the `authorization`
    header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get(f"/teams/{str(uuid.uuid4())}")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_team_detail_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/teams/<team_id>` with an invalid token in the `authorization`
    header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.get(
        f"/users/{str(uuid.uuid4())}", headers=dict(authorization="abcdefg")
    )
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_team_detail_get_non_uuid(client):
    """
    WHEN a get request is made to `/teams/<team_id>` but the team ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided team ID is not a valid
    UUID
    """

    response = client.get(
        "/teams/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError("Team ID abcdefg is not a valid UUID").to_dict()]
    )


def test_team_detail_get_nonexistent(client):
    """
    WHEN a get request is made to `/teams/<team_id>` but no team with the given ID exists
    THEN the response should have a 404 status and indicate that no team with the given ID exists
    """

    team_id = str(uuid.uuid4())
    response = client.get(
        f"/teams/{team_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[NotFoundError(f"No Team exists with the ID {team_id}").to_dict()]
    )


def test_team_detail_get_success(client, team1):
    """
    GIVEN an existing team on the platform
    WHEN a get request is made to `/teams/<team_id>` with the team's ID
    THEN the response should have a 200 status code and return the details of the team
    """

    response = client.get(
        f"/teams/{team1.id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 200
    assert json.loads(response.data.decode()) == {
        "data": dict(marshal(team1, TeamMarshaller.all()))
    }
