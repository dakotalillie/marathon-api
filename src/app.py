import os
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from .controllers.auth import authenticate, identity
from .controllers.users import UserList, UserDetail
from .db import DB


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)


def setup_api(app):
    api = Api(app)
    api.add_resource(UserList, "/users")
    api.add_resource(UserDetail, "/users/<user_id>")


def setup_jwt(app):
    JWT(app, authenticate, identity)


def create_app():
    app = Flask(__name__)
    setup_db(app)
    setup_api(app)
    setup_jwt(app)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0")
