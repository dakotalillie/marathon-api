from flask_restful import Resource, reqparse

from ..db import DB
from ..models import User
from ..utils.is_valid_uuid import is_valid_uuid


class UserDetail(Resource):
    def __init__(self):
        super()
        self.parser = self._make_parser()

    def get(self, user_id):
        if not is_valid_uuid(user_id):
            return (None, 404)
        user = User.query.filter_by(id=user_id).first_or_404()
        return {
            "data": dict(
                id=str(user.id),
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                visibility=user.visibility,
                created_at=str(user.created_at),
                updated_at=str(user.updated_at),
                is_active=user.is_active,
            )
        }

    def patch(self, user_id):
        if not is_valid_uuid(user_id):
            return (None, 404)
        user = User.query.filter_by(id=user_id).first_or_404()
        args = self.parser.parse_args()
        for key, value in args.items():
            if value is not None:
                setattr(user, key, value)
        DB.session.add(user)
        DB.session.commit()
        return (
            {
                "data": dict(
                    id=str(user.id),
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    email=user.email,
                    visibility=user.visibility,
                    created_at=str(user.created_at),
                    updated_at=str(user.updated_at),
                    is_active=user.is_active,
                )
            },
        )

    def delete(self, user_id):
        if not is_valid_uuid(user_id):
            return (None, 404)
        user = User.query.filter_by(id=user_id).first_or_404()
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
