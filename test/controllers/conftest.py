import pytest

from src.app import create_app
from src.db import DB
from src.models import User


@pytest.fixture(name="app")
def app_fixture():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        DB.create_all()
        yield app
        DB.session.close()
        DB.drop_all()


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def existing_user(app):
    user = User(
        first_name="Dakota",
        last_name="Lillie",
        username="dlillie",
        email="dakota.lillie@icloud.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    yield user
