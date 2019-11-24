from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..db import DB
from ..exceptions import BadRequestError, ForbiddenError
from ..models import Team, TeamMembership, User
from ..utils.is_valid_uuid import is_valid_uuid
from ..utils.controller_decorators import call_before, get_resource, format_response


def validate_uuid(*args, team_id):
    if not is_valid_uuid(team_id):
        raise BadRequestError(f"Team ID {team_id} is not a valid UUID")


def validate_permissions(*args, team):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(id=current_user_id).first()
    if (not current_user) or (current_user not in team.members):
        raise ForbiddenError(
            f"User {current_user_id} cannot modify team {team.id} because they are not a member"
        )


def make_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(name="name", nullable=False, location="form")
    return parser


class TeamDetail(Resource):
    def __init__(self):
        super().__init__()
        self.parser = make_parser()

    @jwt_required
    @call_before([validate_uuid])
    @get_resource(Team)
    @format_response(
        {
            "name": "teams",
            "marshaller": Team.marshaller.omit("id"),
            "relationships": [
                {
                    "name": "team_memberships",
                    "marshaller": TeamMembership.marshaller.omit("id"),
                },
                {
                    "name": "users",
                    "related_name": "members",
                    "marshaller": User.marshaller.omit("id"),
                },
            ],
        }
    )
    def get(self, team):
        # pylint: disable=no-self-use
        return team

    @jwt_required
    @call_before([validate_uuid])
    @get_resource(Team)
    @call_before([validate_permissions])
    @format_response(
        {"name": "teams", "marshaller": Team.marshaller.omit("id"),}
    )
    def patch(self, team):
        args = self.parser.parse_args()
        for key, value in args.items():
            if value is not None:
                setattr(team, key, value)
        DB.session.add(team)
        DB.session.commit()
        return team

    @jwt_required
    @call_before([validate_uuid])
    @get_resource(Team)
    @call_before([validate_permissions])
    def delete(self, team):
        # pylint: disable=no-self-use
        DB.session.delete(team)
        DB.session.commit()
        return None, 204
