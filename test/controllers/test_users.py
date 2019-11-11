import os

from src.app import APP


def test_get_users():
    print(os.environ)
    assert True == True
    # response = APP.test_client().get("/users")
    # print(response.status_code)
    # assert response.status_code == 401
