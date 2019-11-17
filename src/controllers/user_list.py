import re

from flask_restful import Resource, reqparse, marshal_with
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..db import DB
from ..exceptions import ConflictError
from ..models import User
from ..marshallers import UserMarshaller


def make_parser():
    parser = reqparse.RequestParser()
    for arg in ("first_name", "last_name", "username", "email", "password"):
        parser.add_argument(name=arg, required=True, nullable=False, location="form")
    return parser


def find_duplicated_field(error):
    return next(
        key
        for key in ("username", "email")
        if re.search(
            f'duplicate key value violates unique constraint "users_{key}_key"',
            str(error),
        )
    )


def check_for_conflict(error, args):
    duplicated_field = find_duplicated_field(error)
    if duplicated_field:
        raise ConflictError(
            f"User with {duplicated_field} {args[duplicated_field]} already exists"
        )


class UserList(Resource):
    def __init__(self):
        super().__init__()
        self.parser = make_parser()

    @jwt_required
    @marshal_with(UserMarshaller.all(), envelope="data")
    def get(self):
        # pylint: disable=no-self-use
        return User.query.all()

    @marshal_with(UserMarshaller.all(), envelope="data")
    def post(self):
        args = self.parser.parse_args()
        user = User(**args)
        DB.session.add(user)
        try:
            DB.session.commit()
        except IntegrityError as error:
            DB.session.rollback()
            check_for_conflict(error, args)
            raise
        return user, 201
