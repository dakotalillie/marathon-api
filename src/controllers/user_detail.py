from flask_restful import Resource, reqparse, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..db import DB
from ..exceptions import BadRequestError, ForbiddenError
from ..models import User
from ..marshallers import UserMarshaller
from ..utils.is_valid_uuid import is_valid_uuid
from ..utils.controller_decorators import call_before, get_resource


def validate_uuid(user_id):
    if not is_valid_uuid(user_id):
        raise BadRequestError(f"User ID {user_id} is not a valid UUID")


def validate_permissions(user_id):
    current_user_id = get_jwt_identity()
    if user_id != current_user_id:
        raise ForbiddenError(
            f"User {current_user_id} does not have permission to modify User {user_id}"
        )


class UserDetail(Resource):
    def __init__(self):
        super().__init__()
        self.parser = self.__make_parser()

    @jwt_required
    @call_before([validate_uuid])
    @get_resource(User)
    @marshal_with(UserMarshaller.all(), envelope="data")
    def get(self, user):
        return user

    @jwt_required
    @call_before([validate_uuid, validate_permissions])
    @get_resource(User)
    @marshal_with(UserMarshaller.all(), envelope="data")
    def patch(self, user):
        args = self.parser.parse_args()
        for key, value in args.items():
            if value is not None:
                setattr(user, key, value)
        DB.session.add(user)
        DB.session.commit()
        return user

    @jwt_required
    @call_before([validate_uuid, validate_permissions])
    @get_resource(User)
    def delete(self, user):
        DB.session.delete(user)
        DB.session.commit()
        return None, 204

    def __make_parser(self):
        parser = reqparse.RequestParser()
        for key in ("first_name", "last_name", "username", "email", "password"):
            parser.add_argument(name=key, type=str, nullable=False, location="form")
        return parser
