from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required


from ..exceptions import BadRequestError
from ..marshallers import TeamMarshaller
from ..models import Team
from ..utils.is_valid_uuid import is_valid_uuid
from ..utils.controller_decorators import call_before, get_resource


def validate_uuid(*args, team_id):
    if not is_valid_uuid(team_id):
        raise BadRequestError(f"Team ID {team_id} is not a valid UUID")


class TeamDetail(Resource):
    @jwt_required
    @call_before([validate_uuid])
    @get_resource(Team)
    @marshal_with(TeamMarshaller.all(), envelope="data")
    def get(self, team):
        # pylint: disable=no-self-use
        return team
