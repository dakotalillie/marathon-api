import os
from operator import itemgetter

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from .controllers import Auth, TeamList, UserList, UserDetail
from .db import DB
from .exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError


def setup_db(app, db_params):
    user, password, host, port, name = itemgetter(
        "user", "password", "host", "port", "name"
    )(db_params)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)


def setup_api(app):
    api = Api(app)
    api.add_resource(Auth, "/auth")
    api.add_resource(TeamList, "/teams")
    api.add_resource(UserList, "/users")
    api.add_resource(UserDetail, "/users/<user_id>")


def setup_jwt(app):
    # pylint: disable=unused-variable
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized(reason):
        return dict(message=reason), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return dict(message=reason), 422


def setup_error_handling(app):
    # pylint: disable=unused-variable
    app.config["BUNDLE_ERRORS"] = True

    @app.errorhandler(BadRequestError)
    @app.errorhandler(ConflictError)
    @app.errorhandler(ForbiddenError)
    @app.errorhandler(NotFoundError)
    def handle_error(error):
        return dict(errors=[error.to_dict()]), error.status_code


def create_app(
    db_user=os.getenv("DB_USER"),
    db_password=os.getenv("DB_PASSWORD"),
    db_host=os.getenv("DB_HOST"),
    db_port=os.getenv("DB_PORT"),
    db_name=os.getenv("DB_NAME"),
):
    app = Flask(__name__)
    setup_db(
        app,
        dict(
            user=db_user, password=db_password, host=db_host, port=db_port, name=db_name
        ),
    )
    setup_api(app)
    setup_jwt(app)
    setup_error_handling(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0")
