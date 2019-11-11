from src.app import APP


def test_get_users():
    response = APP.test_client().get("/users")
    assert response.status_code == 401
