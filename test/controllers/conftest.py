import pytest

from src.app import create_app
from src.db import DB


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
