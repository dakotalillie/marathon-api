from src.db import DB
from src.models import User


def test_auth_success(client):
    user = User(
        first_name="Dakota",
        last_name="Lillie",
        username="dlillie",
        email="dakota.lillie@icloud.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    response = client.post("/auth", data=dict(username="dlillie", password="password"))
    assert response.status_code == 200
