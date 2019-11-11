import uuid
from flask_jwt_extended import create_access_token

from src.db import DB
from src.models import User


def test_user_list_get_without_auth(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_user_list_get_with_auth(client):
    user = User(
        first_name="Dakota",
        last_name="Lillie",
        username="dlillie",
        email="dakota.lillie@icloud.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    response = client.get(
        "/users",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user.id)}"),
    )
    assert response.status_code == 200


def test_user_list_post_malformed_request(client):
    response = client.post("/users", data=dict(first_name="Dakota", last_name="Lillie"))
    assert response.status_code == 400


def test_user_list_post_success(client):
    response = client.post(
        "/users",
        data=dict(
            first_name="Elizabeth",
            last_name="Warren",
            username="ewarren",
            email="ewarren@gmail.com",
            password="abc",
        ),
    )
    assert response.status_code == 201


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
