from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token

from ..exceptions import BadRequestError
from ..models import User


class Auth(Resource):
    def __init__(self):
        super().__init__()
        self.parser = self.__make_parser()

    def post(self):
        args = self.parser.parse_args()
        user = User.query.filter_by(username=args["username"]).first()
        if user and user.has_password(args["password"]):
            return dict(data=dict(access_token=create_access_token(identity=user.id)))
        raise BadRequestError("Invalid credentials")

    def __make_parser(self):
        parser = reqparse.RequestParser()
        for key in ("username", "password"):
            parser.add_argument(
                name=key, required=True, nullable=False, location="form"
            )
        return parser
