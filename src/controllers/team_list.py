from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from ..db import DB
from ..exceptions import BadRequestError
from ..models import Team, TeamMembership, User
from ..utils.controller_decorators import format_response


def make_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(name="name", required=True, nullable=False, location="form")
    parser.add_argument(
        name="team_members",
        required=True,
        nullable=False,
        location="form",
        action="append",
    )
    return parser


class TeamList(Resource):
    def __init__(self):
        super().__init__()
        self.parser = make_parser()

    @jwt_required
    @format_response(
        {
            "name": "teams",
            "marshaller": Team.marshaller.omit("id"),
            "relationships": [
                {
                    "name": "team_memberships",
                    "marshaller": TeamMembership.marshaller.pick("user_id", "team_id"),
                },
                {
                    "name": "users",
                    "related_name": "members",
                    "marshaller": User.marshaller.pick("username"),
                },
            ],
        }
    )
    def get(self):
        # pylint: disable=no-self-use
        return Team.query.all()

    @jwt_required
    @format_response(
        {
            "name": "teams",
            "marshaller": Team.marshaller.omit("id"),
            "relationships": [
                {
                    "name": "team_memberships",
                    "marshaller": TeamMembership.marshaller.pick("user_id", "team_id"),
                },
                {
                    "name": "users",
                    "related_name": "members",
                    "marshaller": User.marshaller.pick("username"),
                },
            ],
        }
    )
    def post(self):
        args = self.parser.parse_args()
        team = Team(name=args.get("name"))
        for user_id in args.get("team_members"):
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise BadRequestError(f"User with id {user_id} does not exist")
            team.members.append(user)
        DB.session.add(team)
        DB.session.commit()
        return team, 201
