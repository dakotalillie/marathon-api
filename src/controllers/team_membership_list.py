from flask import Response
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from ..db import DB
from ..exceptions import BadRequestError
from ..models import Team, User


def make_parser():
    parser = reqparse.RequestParser()
    for arg in ("user", "team"):
        parser.add_argument(name=arg, required=True, nullable=False, location="form")
    return parser


def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequestError(
            f"Cannot complete operation because user {user_id} does not exist"
        )
    return user


def get_team(team_id):
    team = Team.query.filter_by(id=team_id).first()
    if not team:
        raise BadRequestError(
            f"Cannot complete operation because team {team_id} does not exist"
        )
    return team


class TeamMembershipList(Resource):
    def __init__(self):
        super().__init__()
        self.parser = make_parser()

    @jwt_required
    def post(self):
        # pylint: disable=no-self-use
        args = self.parser.parse_args()
        user = get_user(args["user"])
        team = get_team(args["team"])
        team.members.append(user)
        if not DB.session.is_modified(team):
            return Response(status=204)
        DB.session.add(team)
        DB.session.commit()
        return Response(status=201)
