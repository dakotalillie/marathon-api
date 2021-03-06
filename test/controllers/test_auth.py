import json
import pytest

from src.exceptions import BadRequestError
from .utils import get_content_type

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            dict(),
            dict(
                username="Missing required parameter in the post body",
                password="Missing required parameter in the post body",
            ),
        ),
        (
            dict(username="username"),
            dict(password="Missing required parameter in the post body"),
        ),
        (
            dict(password="password"),
            dict(username="Missing required parameter in the post body"),
        ),
    ],
)
def test_auth_post_missing_arguments(client, test_input, expected):
    """
    WHEN a post request is made to the `/auth` endpoint that lacks the requirement arguments
    THEN the response should have a 400 status code and indicate which arguments are missing
    """

    response = client.post("/auth", data=test_input)
    assert get_content_type(response) == "application/vnd.api+json"
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(message=expected)


def test_auth_post_nonexistent_user(client):
    """
    WHEN a post request is made to the `/auth` endpoint for a user that doesn't exist
    THEN the response should have a 400 status code and indicate the credentials were invalid
    """

    response = client.post("/auth", data=dict(username="username", password="password"))
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError("Invalid credentials").to_dict()]
    )


def test_auth_post_incorrect_password(client, user1):
    """
    GIVEN a pre-existing user
    WHEN a post request is made to the `/auth` endpoint with an incorrect password for that user
    THEN the response should have a 400 status code and indicate the credentials were invalid
    """
    response = client.post(
        "/auth", data=dict(username=user1.username, password="wrong_password")
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError("Invalid credentials").to_dict()]
    )


def test_auth_post_success(client, user1):
    """
    GIVEN a pre-existing user
    WHEN a post request is made to the `/auth` endpoint with the correct credentials for that user
    THEN the response should have a 200 status code and include an access token
    """

    # `password` is a write-only field, so we can't reference it from user1
    response = client.post(
        "/auth", data=dict(username=user1.username, password="password")
    )

    assert response.status_code == 200
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode())["data"]["access_token"] is not None
