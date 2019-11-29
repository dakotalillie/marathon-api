import json

from flask_jwt_extended import create_access_token
import pytest

from src.db import DB
from src.exceptions import ConflictError
from src.models import User
from .utils import get_content_type

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_user_list_get_without_auth(client):
    """
    WHEN a get request is made to `/users` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get("/users")
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


def test_user_list_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/users` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.get("/users", headers=dict(authorization="abcdefg"))
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


def test_user_list_get_success(client, user1, team1):
    """
    GIVEN there are existing users on the platform
    WHEN a get request is made to `/users` with valid authorization
    THEN the response should have a 200 status code and return a list of all users on the platform
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    response = client.get(
        "/users",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )
    team_membership = user1.team_memberships[0]
    assert response.status_code == 200
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {"self": "http://localhost/users"},
        "data": [
            {
                "type": "users",
                "id": user1.id,
                "attributes": {
                    "created_at": user1.created_at.isoformat(),
                    "updated_at": user1.updated_at.isoformat(),
                    "is_active": True,
                    "first_name": user1.first_name,
                    "last_name": user1.last_name,
                    "username": user1.username,
                    "email": user1.email,
                    "visibility": user1.visibility,
                },
                "relationships": {
                    "team_memberships": {
                        "data": [{"type": "team_memberships", "id": team_membership.id}]
                    },
                    "teams": {"data": [{"type": "teams", "id": team1.id}]},
                },
                "links": {"self": f"http://localhost/users/{user1.id}"},
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
                "type": "teams",
                "id": team1.id,
                "attributes": {"name": team1.name},
                "links": {"self": f"http://localhost/teams/{team1.id}"},
            },
        ],
    }


def test_user_list_post_missing_parameters(client):
    """
    WHEN a post request is made to `/users` which is missing required fields
    THEN the response should have a 400 status code and indicate which fields are missing
    """

    response = client.post(
        "/users",
        data=dict(
            first_name="first", last_name="last", username="username", email="email"
        ),
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        message=dict(password="Missing required parameter in the post body")
    )


def test_user_list_post_duplicate_email(client, user1):
    """
    GIVEN a pre-existing user
    WHEN a post request is made to `/users` with the same email as that user
    THEN the response should have a 409 status code and indicate that the user already exists
    """

    response = client.post(
        "/users",
        data=dict(
            first_name="first",
            last_name="last",
            username="new_username",
            email=user1.email,
            password="password",
        ),
    )
    assert response.status_code == 409
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[
            ConflictError(f"User with email {user1.email} already exists").to_dict()
        ]
    )


def test_user_list_post_duplicate_username(client, user1):
    """
    GIVEN a pre-existing user
    WHEN a post request is made to `/users` with the same username as that user
    THEN the response should have a 409 status code and indicate that the user already exists
    """

    response = client.post(
        "/users",
        data=dict(
            first_name="first",
            last_name="last",
            username=user1.username,
            email="new_email",
            password="password",
        ),
    )
    assert response.status_code == 409
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[
            ConflictError(
                f"User with username {user1.username} already exists"
            ).to_dict()
        ]
    )


def test_user_list_post_success(client):
    """
    WHEN a post request is made to `/users` with valid parameters
    THEN the response should have a 201 status code and return the data for the newly created user
    """

    response = client.post(
        "/users",
        data=dict(
            first_name="first",
            last_name="last",
            username="username",
            email="email@email.com",
            password="password",
        ),
    )
    user = User.query.filter_by(username="username").first()
    assert response.status_code == 201
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {"self": "http://localhost/users"},
        "data": {
            "type": "users",
            "id": user.id,
            "attributes": {
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "is_active": True,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "visibility": user.visibility,
            },
            "links": {"self": f"http://localhost/users/{user.id}"},
        },
    }
