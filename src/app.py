from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from .controllers.auth import Auth, authenticate, identity
from .controllers.users import UserList, UserDetail
from .db import DB


def setup_app():
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql+psycopg2://postgres:example_password@postgres:5432/postgres"
    app.config["SECRET_KEY"] = "my secret key"
    return app


def setup_api(app):
    api = Api(app)
    # api.add_resource(Auth, "/auth")
    api.add_resource(UserList, "/users")
    api.add_resource(UserDetail, "/users/<user_id>")


if __name__ == "__main__":
    APP = setup_app()
    setup_api(APP)
    DB.init_app(APP)
    JWT(APP, authenticate, identity)
    APP.run(debug=True, host="0.0.0.0")
