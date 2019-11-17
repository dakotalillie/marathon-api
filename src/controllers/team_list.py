from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required

from ..marshallers import TeamMarshaller
from ..models import Team


class TeamList(Resource):
    @jwt_required
    @marshal_with(TeamMarshaller.all(), envelope="data")
    def get(self):
        return Team.query.all()
