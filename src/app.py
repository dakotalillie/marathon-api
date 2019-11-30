import os
from operator import itemgetter

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
from flask_restful import Api

from .controllers import (
    Auth,
    TeamDetail,
    TeamList,
    TeamMembershipDetail,
    TeamMembershipList,
    UserList,
    UserDetail,
    UserTeams,
)
from .db import DB
from .exceptions import (
    make_error_response,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    UnprocessableEntityError,
    NotAcceptableError,
    UnsupportedMediaTypeError,
)


def setup_db(app, db_params):
    user, password, host, port, name = itemgetter(
        "user", "password", "host", "port", "name"
    )(db_params)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    DB.init_app(app)


def setup_api(app):
    api = Api(app)
    api.add_resource(Auth, "/auth")
    api.add_resource(TeamList, "/teams")
    api.add_resource(TeamDetail, "/teams/<team_id>")
    api.add_resource(TeamMembershipList, "/team_memberships")
    api.add_resource(TeamMembershipDetail, "/team_memberships/<team_membership_id>")
    api.add_resource(UserList, "/users")
    api.add_resource(UserDetail, "/users/<user_id>")
    api.add_resource(UserTeams, "/users/<user_id>/teams")


def setup_jwt(app):
    # pylint: disable=unused-variable
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized(reason):
        return make_error_response(UnauthorizedError(reason))

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return make_error_response(UnprocessableEntityError(reason))


def setup_error_handling(app):
    # pylint: disable=unused-variable
    app.config["BUNDLE_ERRORS"] = True

    @app.errorhandler(BadRequestError)
    @app.errorhandler(ConflictError)
    @app.errorhandler(ForbiddenError)
    @app.errorhandler(NotFoundError)
    @app.errorhandler(UnauthorizedError)
    @app.errorhandler(NotAcceptableError)
    @app.errorhandler(UnsupportedMediaTypeError)
    def handle_error(error):
        return make_error_response(error)


def setup_response_headers(app):
    # pylint: disable=unused-variable
    @app.after_request
    def add_content_type(resp):
        resp.headers["Content-Type"] = "application/vnd.api+json"
        return resp


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
    setup_response_headers(app)
    Migrate(app, DB)
    with app.app_context():
        upgrade()
    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0")
