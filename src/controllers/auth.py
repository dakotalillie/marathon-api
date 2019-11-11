from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token

from ..models import User


class Auth(Resource):
    def __init__(self):
        super()
        self.parser = self._make_parser()

    def post(self):
        args = self.parser.parse_args()
        user = User.query.filter_by(username=args["username"]).first()
        if user and user.has_password(args["password"]):
            return dict(access_token=create_access_token(identity=user.id))
        return dict(message="Invalid credentials"), 400

    def _make_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            name="username", required=True, nullable=False, location="form"
        )
        parser.add_argument(
            name="password", required=True, nullable=False, location="form"
        )
        return parser
