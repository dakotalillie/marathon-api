import uuid
import pytest

from src.db import DB
from src.models import User

pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_user_detail_get_non_uuid(client):
    response = client.get("/users/abcdefg")
    assert response.status_code == 404


def test_user_detail_get_nonexistent(client):
    response = client.get(f"/users/{uuid.uuid4().hex}")
    assert response.status_code == 404


def test_user_detail_get_success(client):
    user = User(
        first_name="Dakota",
        last_name="Lillie",
        username="dlillie",
        email="dakota.lillie@icloud.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200


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
