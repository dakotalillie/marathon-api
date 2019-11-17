import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from .controllers import Auth, TeamList, UserList, UserDetail
from .db import DB
from .exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError


def setup_db(app, db_user, db_password, db_host, db_port, db_name):
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)


def setup_api(app):
    api = Api(app)
    api.add_resource(Auth, "/auth")
    api.add_resource(TeamList, "/teams")
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
    setup_db(app, db_user, db_password, db_host, db_port, db_name)
    setup_api(app)
    setup_jwt(app)
    setup_error_handling(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0")
