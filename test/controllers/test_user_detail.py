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
    THEN the response should have a 400 status and indicate that the provide user ID is not a valid UUID
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


def test_user_detail_patch_non_uuid(client):
    response = client.patch("/users/abcdefg", data=dict(first_name="Billy"))
    assert response.status_code == 404


def test_user_detail_patch_nonexistent(client):
    response = client.patch(f"/users/{uuid.uuid4().hex}", data=dict(first_name="Billy"))
    assert response.status_code == 404


def test_user_detail_patch_success(client):
    user = User(
        first_name="Dakota",
        last_name="Lillie",
        username="dlillie",
        email="dakota.lillie@icloud.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    response = client.patch(f"/users/{user.id}", data=dict(first_name="Billy"))
    assert response.status_code == 200
    assert user.first_name == "Billy"


def test_user_detail_delete_non_uuid(client):
    response = client.delete("/users/abcdefg")
    assert response.status_code == 404


def test_user_detail_delete_nonexistent(client):
    response = client.delete(f"/users/{uuid.uuid4().hex}")
    assert response.status_code == 404


def test_user_detail_delete_success(client):
    user = User(
        first_name="Dakota",
        last_name="Lillie",
        username="dlillie",
        email="dakota.lillie@icloud.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    response = client.delete(f"/users/{user.id}")
    assert response.status_code == 204
