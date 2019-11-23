from flask_restful import Resource, reqparse, marshal_with
from flask_jwt_extended import jwt_required

from ..db import DB
from ..exceptions import BadRequestError
from ..models import Team, User


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
    @marshal_with(Team.marshaller.all(), envelope="data")
    def get(self):
        # pylint: disable=no-self-use
        return Team.query.all()

    @jwt_required
    @marshal_with(Team.marshaller.all(), envelope="data")
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
