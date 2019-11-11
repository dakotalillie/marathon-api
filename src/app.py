import os
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from .controllers.auth import authenticate, identity
from .controllers.users import UserList, UserDetail
from .db import DB


def setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    return app


def setup_api(app):
    api = Api(app)
    api.add_resource(UserList, "/users")
    api.add_resource(UserDetail, "/users/<user_id>")


APP = setup_app()
setup_api(APP)
DB.init_app(APP)
JWT(APP, authenticate, identity)

if __name__ == "__main__":
    APP.run(debug=True, host="0.0.0.0")
