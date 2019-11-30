import json
from uuid import uuid4

from flask_jwt_extended import create_access_token
import pytest

from src.db import DB
from src.models import TeamMembership
from .utils import get_content_type

# pylint: disable=invalid-name
pytestmark = [pytest.mark.integration, pytest.mark.controllers]


def test_user_teams_get_without_auth(client, user1):
    """
    WHEN a get request is made to `/users/<user_id>/teams` without a token in the `Authorization`
    header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get(
        f"/users/{user1.id}/teams", headers={"Accept": "application/vnd.api+json"},
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


def test_user_teams_get_with_invalid_auth(client, user1):
    """
    WHEN a get request is made to `/users/<user_id>/teams` with an invalid token in the
    `Authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.get(
        f"/users/{user1.id}/teams",
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


def test_user_teams_get_invalid_accept_header(client, user1):
    """
    WHEN a get request is made to `/users/<user_id>/teams` and the `Accept` header is not correctly
    set
    THEN the response should have a 406 status code and indicate that the `Accept` header is not
    correctly set
    """

    response = client.get(
        f"/users/{user1.id}/teams",
        headers={"Authorization": f"Bearer {create_access_token(identity=user1.id)}"},
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


def test_user_teams_get_non_uuid(client, user1):
    """
    WHEN a get request is made to `/users/<user_id>/teams` but the user ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided user ID is not a valid
    UUID
    """

    response = client.get(
        "/users/abcdefg/teams",
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "User ID abcdefg is not a valid UUID",
            }
        ]
    }


def test_user_teams_get_nonexistent(client, user1):
    """
    WHEN a get request is made to `/users/<user_id>/teams` but no user with the given ID exists
    THEN the response should have a 404 status and indicate that no user with the given ID exists
    """

    user_id = str(uuid4())
    response = client.get(
        f"/users/{user_id}/teams",
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )
    assert response.status_code == 404
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 404,
                "title": "Not Found",
                "detail": f"No User exists with the ID {user_id}",
            }
        ]
    }


def test_user_teams_get_success(client, user1, team1):
    """
    GIVEN a user on the platform
    WHEN a get request is made to `/users/<user_id>` with the user's ID
    THEN the response should have a 200 status code and return a list of the teams the user is a
    member of
    """

    DB.session.add(
        TeamMembership(
            user_id=user1.id, team_id=team1.id, created_by=user1.id, updated_by=user1.id
        )
    )
    DB.session.commit()

    response = client.get(
        f"/users/{user1.id}/teams",
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )

    assert response.status_code == 200
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {"self": f"http://localhost/users/{user1.id}/teams"},
        "data": [
            {
                "type": "teams",
                "id": team1.id,
                "attributes": {
                    "createdAt": team1.created_at.isoformat(),
                    "name": team1.name,
                    "updatedAt": team1.updated_at.isoformat(),
                },
                "relationships": {
                    "createdBy": {
                        "links": {"related": f"http://localhost/users/{user1.id}"},
                        "data": {"type": "users", "id": user1.id},
                    },
                    "updatedBy": {
                        "links": {"related": f"http://localhost/users/{user1.id}"},
                        "data": {"type": "users", "id": user1.id},
                    },
                    "members": {
                        "links": {
                            "self": f"http://localhost/teams/{team1.id}/relationships/members",
                            "related": f"http://localhost/teams/{team1.id}/members",
                        },
                        "data": [{"type": "users", "id": user1.id}],
                    },
                },
                "links": {"self": f"http://localhost/teams/{team1.id}"},
            },
        ],
    }
