from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..db import DB
from ..exceptions import BadRequestError, ForbiddenError
from ..models import Team, TeamMembership, User
from ..utils.is_valid_uuid import is_valid_uuid
from ..utils.controller_decorators import call_before, get_resource, format_response
from ..utils.controller_validators import (
    validate_accept_header,
    validate_content_type_header,
)


def validate_uuid(*args, user_id):
    if not is_valid_uuid(user_id):
        raise BadRequestError(f"User ID {user_id} is not a valid UUID")


def validate_permissions(*args, user_id):
    current_user_id = get_jwt_identity()
    if user_id != current_user_id:
        raise ForbiddenError(
            f"User {current_user_id} does not have permission to modify User {user_id}"
        )


def make_parser():
    parser = reqparse.RequestParser()
    for key in ("first_name", "last_name", "username", "email", "password"):
        parser.add_argument(name=key, nullable=False, location="json")
    return parser


class UserDetail(Resource):
    def __init__(self):
        super().__init__()
        self.parser = make_parser()

    @jwt_required
    @call_before([validate_accept_header, validate_uuid])
    @get_resource(User)
    @format_response(
        {
            "name": "users",
            "marshaller": User.marshaller.omit("id"),
            "relationships": [
                {
                    "name": "team_memberships",
                    "marshaller": TeamMembership.marshaller.omit("id"),
                },
                {"name": "teams", "marshaller": Team.marshaller.omit("id"),},
            ],
        }
    )
    def get(self, user):
        # pylint: disable=no-self-use
        return user

    @jwt_required
    @call_before(
        [
            validate_accept_header,
            validate_content_type_header,
            validate_uuid,
            validate_permissions,
        ]
    )
    @get_resource(User)
    @format_response(
        {"name": "users", "marshaller": User.marshaller.omit("id"),}
    )
    def patch(self, user):
        args = self.parser.parse_args()
        for key, value in args.items():
            if value is not None:
                setattr(user, key, value)
        DB.session.add(user)
        DB.session.commit()
        return user

    @jwt_required
    @call_before([validate_accept_header, validate_uuid, validate_permissions])
    @get_resource(User)
    def delete(self, user):
        # pylint: disable=no-self-use
        DB.session.delete(user)
        DB.session.commit()
        return None, 204
