import json
import uuid

import pytest

from src.db import DB
from src.models import User
from flask_jwt_extended import create_access_token

pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_user_detail_get_without_auth(client):
    """
    WHEN a get request is made to `/users/<user_id>` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get("/users/abcdefg")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_user_detail_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/users/<user_id>` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is malformed
    """

    response = client.get("/users/abcdefg", headers=dict(authorization="abcdefg"))
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_user_detail_get_non_uuid(client, existing_user):
    """
    WHEN a get request is made to `/users/<user_id>` but the user ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided user ID is not a valid UUID
    """

    response = client.get(
        "/users/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=400,
                title="Invalid UUID",
                detail=f"User ID abcdefg is not a valid UUID",
            )
        ]
    )


def test_user_detail_get_nonexistent(client, existing_user):
    """
    WHEN a get request is made to `/users/<user_id>` but no user with the given ID exists
    THEN the response should have a 404 status and indicate that no user with the given ID exists
    """

    user_id = str(uuid.uuid4())
    response = client.get(
        f"/users/{user_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=404,
                title="User not found",
                detail=f"No User exists with the ID {user_id}",
            )
        ]
    )


def test_user_detail_get_success(client, existing_user):
    """
    GIVEN an existing user on the platform
    WHEN a get request is made to `/users/<user_id>` with the user's ID
    THEN the response should have a 200 status code and return the details of the user
    """

    response = client.get(
        f"/users/{existing_user.id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 200
    assert json.loads(response.data.decode()) == dict(
        data=dict(
            id=str(existing_user.id),
            first_name=existing_user.first_name,
            last_name=existing_user.last_name,
            username=existing_user.username,
            email=existing_user.email,
            visibility=existing_user.visibility,
            created_at=str(existing_user.created_at),
            updated_at=str(existing_user.updated_at),
            is_active=existing_user.is_active,
        )
    )


def test_user_detail_patch_without_auth(client):
    """
    WHEN a patch request is made to `/users/<user_id>` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.patch("/users/abcdefg")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_user_detail_patch_with_invalid_auth(client):
    """
    WHEN a patch request is made to `/users/<user_id>` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is malformed
    """

    response = client.patch("/users/abcdefg", headers=dict(authorization="abcdefg"))
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_user_detail_patch_non_uuid(client, existing_user):
    """
    WHEN a patch request is made to `/users/<user_id>` but the user ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided user ID is not a valid UUID
    """

    response = client.patch(
        "/users/abcdefg",
        data=dict(first_name="first"),
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=400,
                title="Invalid UUID",
                detail=f"User ID abcdefg is not a valid UUID",
            )
        ]
    )


def test_user_detail_patch_nonexistent(client, existing_user):
    """
    WHEN a patch request is made to `/users/<user_id>` but no user with the given ID exists
    THEN the response should have a 404 status and indicate that no user with the given ID exists
    """

    user_id = str(uuid.uuid4())
    response = client.patch(
        f"/users/{user_id}",
        data=dict(first_name="first"),
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=404,
                title="User not found",
                detail=f"No User exists with the ID {user_id}",
            )
        ]
    )


def test_user_detail_patch_different_user(client, existing_user, user2):
    """
    WHEN a patch request is made to `/users/<user_id>` with a token for a different user than the one in the URI
    THEN the response should have a 403 status code and indicate that the operation is forbidden
    """

    response = client.patch(
        f"/users/{existing_user.id}",
        data=dict(first_name="updated_first"),
        headers=dict(authorization=f"Bearer {create_access_token(identity=user2.id)}"),
    )
    assert response.status_code == 403
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=403,
                title="Forbidden Operation",
                detail=f"User {user2.id} does not have permission to modify User {existing_user.id}",
            )
        ]
    )


def test_user_detail_patch_success(client, existing_user):
    """
    GIVEN an existing user on the platform
    WHEN a patch request is made to `/users/<user_id>` with the user's ID
    THEN the response should have a 200 status code and return the updated details of the user
    """

    response = client.patch(
        f"/users/{existing_user.id}",
        data=dict(first_name="updated_first"),
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 200
    assert (
        User.query.filter_by(id=existing_user.id).first().first_name == "updated_first"
    )
    assert json.loads(response.data.decode()) == dict(
        data=dict(
            id=str(existing_user.id),
            first_name=existing_user.first_name,
            last_name=existing_user.last_name,
            username=existing_user.username,
            email=existing_user.email,
            visibility=existing_user.visibility,
            created_at=str(existing_user.created_at),
            updated_at=str(existing_user.updated_at),
            is_active=existing_user.is_active,
        )
    )


def test_user_detail_delete_without_auth(client, existing_user):
    """
    WHEN a delete request is made to `/users/<user_id>` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.delete(f"/users/{existing_user.id}")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == dict(
        message="Missing Authorization Header"
    )


def test_user_detail_delete_with_invalid_auth(client, existing_user):
    """
    WHEN a delete request is made to `/users/<user_id>` with an invalid token in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is malformed
    """

    response = client.delete(
        f"/users/{existing_user.id}", headers=dict(authorization="abcdefg")
    )
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == dict(
        message="Bad Authorization header. Expected value 'Bearer <JWT>'"
    )


def test_user_detail_delete_non_uuid(client, existing_user):
    """
    WHEN a delete request is made to `/users/<user_id>` but the user ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided user ID is not a valid UUID
    """

    response = client.delete(
        "/users/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=400,
                title="Invalid UUID",
                detail=f"User ID abcdefg is not a valid UUID",
            )
        ]
    )


def test_user_detail_delete_nonexistent(client, existing_user):
    """
    WHEN a delete request is made to `/users/<user_id>` but no user with the given ID exists
    THEN the response should have a 404 status and indicate that no user with the given ID exists
    """

    user_id = str(uuid.uuid4())
    response = client.delete(
        f"/users/{user_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=404,
                title="User not found",
                detail=f"No User exists with the ID {user_id}",
            )
        ]
    )


def test_user_detail_delete_different_user(client, existing_user, user2):
    """
    WHEN a delete request is made to `/users/<user_id>` with a token for a different user than the one in the URI
    THEN the response should have a 403 status code and indicate that the operation is forbidden
    """

    response = client.delete(
        f"/users/{existing_user.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user2.id)}"),
    )
    assert response.status_code == 403
    assert json.loads(response.data.decode()) == dict(
        errors=[
            dict(
                status=403,
                title="Forbidden Operation",
                detail=f"User {user2.id} does not have permission to modify User {existing_user.id}",
            )
        ]
    )


def test_user_detail_delete_success(client, existing_user):
    """
    GIVEN an existing user on the platform
    WHEN a delete request is made to `/users/<user_id>` with the user's ID
    THEN the response should have a 204 status code
    """

    response = client.delete(
        f"/users/{existing_user.id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=existing_user.id)}"
        ),
    )
    assert response.status_code == 204
    assert len(response.data) is 0