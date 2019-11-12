import re

from flask_restful import Resource, reqparse, marshal_with, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..db import DB
from ..exceptions import ConflictError
from ..models import User
from ..marshallers import UserMarshaller


class UserList(Resource):
    def __init__(self):
        super()
        self.parser = self.__make_parser()

    @jwt_required
    @marshal_with(UserMarshaller.all(), envelope="data")
    def get(self):
        return User.query.all()

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
                raise ConflictError(
                    f"User with {duplicated_field} {args[duplicated_field]} already exists"
                )
            raise
        return marshal(user, UserMarshaller.all(), envelope="data"), 201

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
