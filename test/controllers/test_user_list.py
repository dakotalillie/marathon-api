import json

from flask_jwt_extended import create_access_token
from flask_restful import marshal
import pytest

from src.exceptions import ConflictError
from src.models import User
from src.marshallers import UserMarshaller

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
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_user_list_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/users` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.get("/users", headers=dict(authorization="abcdefg"))
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_user_list_get_success(client, user1):
    """
    GIVEN there are existing users on the platform
    WHEN a get request is made to `/users` with valid authorization
    THEN the response should have a 200 status code and return a list of all users on the platform
    """

    response = client.get(
        "/users",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )
    assert response.status_code == 200
    assert json.loads(response.data.decode()) == {
        "data": [dict(marshal(user1, UserMarshaller.all()))]
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
    assert json.loads(response.data.decode()) == {
        "data": dict(marshal(user, UserMarshaller.all()))
    }
