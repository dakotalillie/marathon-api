import uuid
import pytest

from src.app import create_app
from src.models import User


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_user_list_get_without_auth(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_user_list_post_malformed_request(client):
    response = client.post("/users", data=dict(first_name="Dakota", last_name="Lillie"))
    assert response.status_code == 400


@pytest.mark.skip(reason="need to be able to clean this up")
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
    user = User.query.filter_by(username="dlillie").first()
    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200


def test_user_detail_patch_non_uuid(client):
    response = client.patch("/users/abcdefg", data=dict(first_name="Billy"))
    assert response.status_code == 404


def test_user_detail_patch_nonexistent(client):
    response = client.patch(f"/users/{uuid.uuid4().hex}", data=dict(first_name="Billy"))
    assert response.status_code == 404


def test_user_detail_patch_success(client):
    user = User.query.filter_by(username="dlillie").first()
    response = client.patch(f"/users/{user.id}", data=dict(first_name="Billy"))
    assert response.status_code == 200
    assert user.first_name == "Billy"


def test_user_detail_delete_non_uuid(client):
    response = client.delete("/users/abcdefg")
    assert response.status_code == 404


def test_user_detail_delete_nonexistent(client):
    response = client.delete(f"/users/{uuid.uuid4().hex}")
    assert response.status_code == 404


@pytest.mark.skip(reason="need to be able to clean this up")
def test_user_detail_delete_success(client):
    user = User.query.filter_by(username="ewarren").first()
    response = client.delete(f"/users/{user.id}")
    assert response.status_code == 204
