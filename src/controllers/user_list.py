import re

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..db import DB
from ..models import User


class UserList(Resource):
    def __init__(self):
        super()
        self.parser = self.__make_parser()

    @jwt_required
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
        user = User(**args)
        DB.session.add(user)
        try:
            DB.session.commit()
        except IntegrityError as error:
            DB.session.rollback()
            duplicated_field = self.__find_duplicated_field(error)
            if duplicated_field:
                return self.__get_duplicate_error_response(
                    duplicated_field, args[duplicated_field]
                )
            raise
        return (
            dict(
                data=dict(
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
            ),
            201,
        )

    def __make_parser(self):
        parser = reqparse.RequestParser()
        for arg in ("first_name", "last_name", "username", "email", "password"):
            parser.add_argument(
                name=arg, required=True, nullable=False, location="form"
            )
        return parser

    def __find_duplicated_field(self, error):
        return next(
            key
            for key in ("username", "email")
            if re.search(
                f'duplicate key value violates unique constraint "users_{key}_key"',
                str(error),
            )
        )

    def __get_duplicate_error_response(self, duplicated_field, value):
        return (
            dict(
                errors=[
                    dict(
                        status=409,
                        title="User already exists",
                        detail=f"User with {duplicated_field} {value} already exists",
                    )
                ]
            ),
            409,
        )
