import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from .controllers.auth import Auth
from .controllers.user_list import UserList
from .controllers.user_detail import UserDetail
from .db import DB
from .exceptions import ForbiddenError, InvalidUUIDError, NotFoundError


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)


def setup_api(app):
    api = Api(app)
    api.add_resource(Auth, "/auth")
    api.add_resource(UserList, "/users")
    api.add_resource(UserDetail, "/users/<user_id>")


def setup_jwt(app):
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized(reason):
        return dict(message=reason), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return dict(message=reason), 422


def setup_error_handling(app):
    app.config["BUNDLE_ERRORS"] = True

    def handle_error(error):
        return dict(errors=[error.to_dict()]), error.status_code

    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        return handle_error(error)

    @app.errorhandler(InvalidUUIDError)
    def handle_invalid_uuid_error(error):
        return handle_error(error)

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        return handle_error(error)


def create_app():
    app = Flask(__name__)
    setup_db(app)
    setup_api(app)
    setup_jwt(app)
    setup_error_handling(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0")
