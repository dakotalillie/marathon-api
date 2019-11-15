import pytest

from src.app import create_app
from src.db import DB
from src.models import User


@pytest.fixture(name="app")
def app_fixture():
    app = create_app(db_name="marathon_test")
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
def user1(app):
    user = User(
        first_name="First",
        last_name="Last",
        username="username",
        email="me@email.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    yield user


@pytest.fixture
def user2(app):
    user = User(
        first_name="user2 first name",
        last_name="user2 last name",
        username="user2",
        email="user2@email.com",
        password="password",
    )
    DB.session.add(user)
    DB.session.commit()
    yield user
