from flask_restful import Resource, reqparse
import bcrypt

from ..models import User


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return user


def identity(payload):
    user_id = payload["identity"]
    return User.query.filter_by(id=user_id).first()


class Auth(Resource):
    def __init__(self):
        super()
        self.parser = self._make_parser()

    def post(self):
        args = self.parser.parse_args()
        user = User.query.filter_by(username=args["username"]).first_or_404()
        if bcrypt.checkpw(
            args["password"].encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            return True
        return False

    def _make_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument(name="username", required=True, type=str, nullable=False)
        parser.add_argument(name="password", required=True, type=str, nullable=False)
        return parser
