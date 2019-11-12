import functools

from flask_restful import Resource, reqparse, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..db import DB
from ..exceptions import BadRequestError, ForbiddenError, NotFoundError
from ..models import User
from ..marshallers import UserMarshaller
from ..utils.is_valid_uuid import is_valid_uuid


def validate_uuid(user_id):
    if not is_valid_uuid(user_id):
        raise BadRequestError(f"User ID {user_id} is not a valid UUID")


def validate_permissions(user_id):
    current_user_id = get_jwt_identity()
    if user_id != current_user_id:
        raise ForbiddenError(
            f"User {current_user_id} does not have permission to modify User {user_id}"
        )


def validate(validators):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs["user_id"]
            for validator in validators:
                validator(user_id)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def with_user(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise NotFoundError(f"No User exists with the ID {user_id}")
        return func(*args, user=user)

    return wrapper


class UserDetail(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.parser = self.__make_parser()

    @jwt_required
    @validate([validate_uuid])
    @with_user
    @marshal_with(UserMarshaller.all(), envelope="data")
    def get(self, user):
        return user

    @jwt_required
    @validate([validate_uuid, validate_permissions])
    @with_user
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
    @validate([validate_uuid, validate_permissions])
    @with_user
    def delete(self, user):
        DB.session.delete(user)
        DB.session.commit()
        return None, 204

    def __make_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument(name="first_name", type=str, nullable=False)
        parser.add_argument(name="last_name", type=str, nullable=False)
        parser.add_argument(name="username", type=str, nullable=False)
        parser.add_argument(name="email", type=str, nullable=False)
        parser.add_argument(name="password", type=str, nullable=False)
        return parser
