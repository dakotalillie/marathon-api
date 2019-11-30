import json
import uuid

from flask_jwt_extended import create_access_token
import pytest

from src.db import DB
from src.exceptions import BadRequestError
from src.models import Team
from .utils import get_content_type

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_team_list_get_without_auth(client):
    """
    WHEN a get request is made to `/teams` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get("/teams", headers={"Accept": "application/vnd.api+json"})
    assert response.status_code == 401
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 401,
                "title": "Unauthorized",
                "detail": "Missing Authorization Header",
            }
        ]
    }


def test_team_list_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/teams` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header
    is malformed
    """

    response = client.get(
        "/teams",
        headers={"Accept": "application/vnd.api+json", "Authorization": "abcdefg"},
    )
    assert response.status_code == 422
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 422,
                "title": "Unprocessable Entity",
                "detail": "Bad Authorization header. Expected value 'Bearer <JWT>'",
            }
        ]
    }


def test_team_list_get_invalid_accept_header(client):
    """
    WHEN a get request is made to `/teams` and the `ACCEPT` header is not correctly set
    THEN the response should have a 406 status code and indicate that the `ACCEPT` header is not
    correctly set
    """

    response = client.get(
        "/teams",
        headers={
            "Authorization": f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        },
    )
    assert response.status_code == 406
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 406,
                "title": "Not Acceptable",
                "detail": "'Accept' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_team_list_get_success(client, user1, team1):
    """
    GIVEN there are existing teams on the platform
    WHEN a get request is made to `/teams` with valid authorization
    THEN the response should have a 200 status code and return a list of all users on the platform
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    response = client.get(
        "/teams",
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )
    team_membership = user1.team_memberships[0]
    assert response.status_code == 200
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {"self": "http://localhost/teams"},
        "data": [
            {
                "type": "teams",
                "id": team1.id,
                "attributes": {
                    "name": team1.name,
                    "created_at": team1.created_at.isoformat(),
                    "created_by": user1.id,
                    "updated_at": team1.updated_at.isoformat(),
                    "updated_by": user1.id,
                    "is_active": True,
                },
                "relationships": {
                    "team_memberships": {
                        "data": [{"type": "team_memberships", "id": team_membership.id}]
                    },
                    "members": {"data": [{"type": "users", "id": user1.id}]},
                },
                "links": {"self": f"http://localhost/teams/{team1.id}"},
            }
        ],
        "included": [
            {
                "type": "team_memberships",
                "id": team_membership.id,
                "attributes": {"user_id": user1.id, "team_id": team1.id},
                "links": {
                    "self": f"http://localhost/team_memberships/{team_membership.id}"
                },
            },
            {
                "type": "users",
                "id": user1.id,
                "attributes": {"username": user1.username},
                "links": {"self": f"http://localhost/users/{user1.id}"},
            },
        ],
    }


def test_team_list_post_without_auth(client, user1):
    """
    WHEN a post request is made to `/teams` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1", "team_members": [user1.id]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 401
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 401,
                "title": "Unauthorized",
                "detail": "Missing Authorization Header",
            }
        ]
    }


def test_team_list_post_with_invalid_auth(client, user1):
    """
    WHEN a post request is made to `/teams` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header
    is malformed
    """

    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1", "team_members": [user1.id]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": "abcdefg",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 422
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 422,
                "title": "Unprocessable Entity",
                "detail": "Bad Authorization header. Expected value 'Bearer <JWT>'",
            }
        ]
    }


def test_team_list_post_invalid_accept_header(client, user1):
    """
    WHEN a post request is made to `/teams` and the `ACCEPT` header is not correctly set
    THEN the response should have a 406 status code and indicate that the `ACCEPT` header is not
    correctly set
    """

    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1", "team_members": [user1.id]}),
        headers={
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 406
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 406,
                "title": "Not Acceptable",
                "detail": "'Accept' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_team_list_post_invalid_content_type_header(client, user1):
    """
    WHEN a post request is made to `/teams` and the `Content-Type` header is not correctly set
    THEN the response should have a 415 status code and indicate that the `Content-Type` header is
    not correctly set
    """

    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1", "team_members": [user1.id]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )
    assert response.status_code == 415
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 415,
                "title": "Unsupported Media Type",
                "detail": "'Content-Type' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_team_list_post_missing_parameters(client, user1):
    """
    WHEN a post request is made to `/teams` which is missing required fields
    THEN the response should have a 400 status code and indicate which fields are missing
    """

    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1"}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        message=dict(team_members="Missing required parameter in the JSON body")
    )


def test_team_list_post_no_team_members(client, user1):
    """
    WHEN a post request is made to `/teams` with no user ids in the `team_members` parameter
    THEN the response should have a 400 status code and indicate that at least one team member is
    required
    """

    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1", "team_members": []}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        message=dict(team_members="Missing required parameter in the JSON body")
    )


def test_team_list_post_invalid_team_members(client, user1):
    """
    WHEN a post request is made to `/teams` with an id in the `team_members` parameter for a
    non-existant user
    THEN the response should have a 400 status code and indicate that the user with the id does not
    exist
    """

    user_id = str(uuid.uuid4())
    response = client.post(
        "/teams",
        data=json.dumps({"name": "team 1", "team_members": [user_id]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
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
        data=json.dumps({"name": "team 1", "team_members": [user1.id]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    team = Team.query.filter_by(name="team 1").first()
    team_membership = user1.team_memberships[0]
    assert response.status_code == 201
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {"self": "http://localhost/teams"},
        "data": {
            "type": "teams",
            "id": team.id,
            "attributes": {
                "name": team.name,
                "created_at": team.created_at.isoformat(),
                "created_by": user1.id,
                "updated_at": team.updated_at.isoformat(),
                "updated_by": user1.id,
                "is_active": True,
            },
            "relationships": {
                "team_memberships": {
                    "data": [{"type": "team_memberships", "id": team_membership.id}]
                },
                "members": {"data": [{"type": "users", "id": user1.id}]},
            },
            "links": {"self": f"http://localhost/teams/{team.id}"},
        },
        "included": [
            {
                "type": "team_memberships",
                "id": team_membership.id,
                "attributes": {"user_id": user1.id, "team_id": team.id},
                "links": {
                    "self": f"http://localhost/team_memberships/{team_membership.id}"
                },
            },
            {
                "type": "users",
                "id": user1.id,
                "attributes": {"username": user1.username},
                "links": {"self": f"http://localhost/users/{user1.id}"},
            },
        ],
    }
