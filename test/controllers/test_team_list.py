import json
import uuid

from flask_jwt_extended import create_access_token
from flask_restful import marshal
import pytest

from src.exceptions import BadRequestError
from src.marshallers import TeamMarshaller
from src.models import Team

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


def test_team_list_post_without_auth(client):
    """
    WHEN a post request is made to `/teams` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.post(
        "/teams", data=dict(name="team 1", team_members=[str(uuid.uuid4())]),
    )
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_team_list_post_with_invalid_auth(client):
    """
    WHEN a post request is made to `/teams` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is malformed
    """

    response = client.post(
        "/teams",
        data=dict(name="team 1", team_members=[str(uuid.uuid4())]),
        headers=dict(authorization="abcdefg"),
    )
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_team_list_post_missing_parameters(client):
    """
    WHEN a post request is made to `/teams` which is missing required fields
    THEN the response should have a 400 status code and indicate which fields are missing
    """

    response = client.post(
        "/teams",
        data=dict(name="team 1"),
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        message=dict(team_members="Missing required parameter in the post body")
    )


def test_team_list_post_no_team_members(client):
    """
    WHEN a post request is made to `/teams` with no user ids in the `team_members` parameter
    THEN the response should have a 400 status code and indicate that at least one team member is required
    """

    response = client.post(
        "/teams",
        data=dict(name="team 1", team_members=[]),
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        message=dict(team_members="Missing required parameter in the post body")
    )


def test_team_list_post_invalid_team_members(client):
    """
    WHEN a post request is made to `/teams` with an id in the `team_members` parameter for a non-existant user
    THEN the response should have a 400 status code and indicate that the user with the id does not exist
    """

    user_id = str(uuid.uuid4())
    response = client.post(
        "/teams",
        data=dict(name="team 1", team_members=[user_id]),
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError(f"User with id {user_id} does not exist").to_dict()]
    )


def test_team_list_post_success(client, user1):
    """
    WHEN a post request is made to `/teams` with valid parameters
    THEN the response should have a 201 status code and return the data for the newly created team
    """

    response = client.post(
        "/teams",
        data=dict(name="team 1", team_members=[user1.id]),
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )
    team = Team.query.filter_by(name="team 1").first()
    assert response.status_code == 201
    assert json.loads(response.data.decode()) == {
        "data": dict(marshal(team, TeamMarshaller.all()))
    }
