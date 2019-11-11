from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import bcrypt

from ..db import DB
from ..models import User


class UserList(Resource):
    def __init__(self):
        super()
        self.parser = self._make_parser()

    @jwt_required()
    def get(self):
        return {
            "data": [
                dict(
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
                for user in User.query.all()
            ],
        }

    def post(self):
        args = self.parser.parse_args()
        user = User(
            **{k: v for k, v in args.items() if k != "password"},
            password_hash=bcrypt.hashpw(
                args["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
        )
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
            201,
        )

    def _make_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument(name="first_name", required=True, type=str, nullable=False)
        parser.add_argument(name="last_name", required=True, type=str, nullable=False)
        parser.add_argument(name="username", required=True, type=str, nullable=False)
        parser.add_argument(name="email", required=True, type=str, nullable=False)
        parser.add_argument(name="password", required=True, type=str, nullable=False)
        return parser


class UserDetail(Resource):
    def __init__(self):
        super()
        self.parser = self._make_parser()

    def get(self, user_id):
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
        user = User.query.filter_by(id=user_id).first_or_404()
        args = self.parser.parse_args()
        for key, value in args.items():
            if value is None:
                continue
            if key == "password":
                user.password_hash = bcrypt.hashpw(
                    value.encode("utf-8"), bcrypt.gensalt()
                )
            else:
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
