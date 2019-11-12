from flask_restful import Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..db import DB
from ..models import User
from ..marshallers import UserMarshaller
from ..utils.is_valid_uuid import is_valid_uuid


class UserDetail(Resource):
    def __init__(self):
        super()
        self.parser = self._make_parser()

    @jwt_required
    def get(self, user_id):
        if not is_valid_uuid(user_id):
            return (
                dict(
                    errors=[
                        dict(
                            status=400,
                            title="Invalid UUID",
                            detail=f"User ID {user_id} is not a valid UUID",
                        )
                    ]
                ),
                400,
            )
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return (
                dict(
                    errors=[
                        dict(
                            status=404,
                            title="User not found",
                            detail=f"No User exists with the ID {user_id}",
                        )
                    ]
                ),
                404,
            )
        return marshal(user, UserMarshaller.all(), envelope="data")

    @jwt_required
    def patch(self, user_id):
        if not is_valid_uuid(user_id):
            return (
                dict(
                    errors=[
                        dict(
                            status=400,
                            title="Invalid UUID",
                            detail=f"User ID {user_id} is not a valid UUID",
                        )
                    ]
                ),
                400,
            )
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return (
                dict(
                    errors=[
                        dict(
                            status=404,
                            title="User not found",
                            detail=f"No User exists with the ID {user_id}",
                        )
                    ]
                ),
                404,
            )
        current_user_id = get_jwt_identity()
        if user.id != current_user_id:
            return (
                dict(
                    errors=[
                        dict(
                            status=403,
                            title="Forbidden Operation",
                            detail=f"User {current_user_id} does not have permission to modify User {user.id}",
                        )
                    ]
                ),
                403,
            )
        args = self.parser.parse_args()
        for key, value in args.items():
            if value is not None:
                setattr(user, key, value)
        DB.session.add(user)
        DB.session.commit()
        return marshal(user, UserMarshaller.all(), envelope="data")

    @jwt_required
    def delete(self, user_id):
        if not is_valid_uuid(user_id):
            return (
                dict(
                    errors=[
                        dict(
                            status=400,
                            title="Invalid UUID",
                            detail=f"User ID {user_id} is not a valid UUID",
                        )
                    ]
                ),
                400,
            )
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return (
                dict(
                    errors=[
                        dict(
                            status=404,
                            title="User not found",
                            detail=f"No User exists with the ID {user_id}",
                        )
                    ]
                ),
                404,
            )
        current_user_id = get_jwt_identity()
        if user.id != current_user_id:
            print("hi!")
            return (
                dict(
                    errors=[
                        dict(
                            status=403,
                            title="Forbidden Operation",
                            detail=f"User {current_user_id} does not have permission to modify User {user.id}",
                        )
                    ]
                ),
                403,
            )
        DB.session.delete(user)
        DB.session.commit()
        return None, 204

    def _make_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument(name="first_name", type=str, nullable=False)
        parser.add_argument(name="last_name", type=str, nullable=False)
        parser.add_argument(name="username", type=str, nullable=False)
        parser.add_argument(name="email", type=str, nullable=False)
        parser.add_argument(name="password", type=str, nullable=False)
        return parser
