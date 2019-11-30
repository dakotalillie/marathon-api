from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from ..exceptions import BadRequestError
from ..models import User, Team
from ..utils.controller_decorators import call_before, get_resource
from ..utils.controller_validators import validate_accept_header
from ..utils.is_valid_uuid import is_valid_uuid


def validate_uuid(*args, user_id):
    if not is_valid_uuid(user_id):
        raise BadRequestError(f"User ID {user_id} is not a valid UUID")


def make_team_resource_object(team):
    return {
        "type": "teams",
        "id": team.id,
        "links": {"self": f"{request.host_url}teams/{team.id}"},
        "attributes": {
            "createdAt": team.created_at.isoformat(),
            "updatedAt": team.updated_at.isoformat(),
            "name": team.name,
        },
        "relationships": {
            "createdBy": {
                "links": {"related": f"{request.host_url}users/{team.created_by}"},
                "data": {"type": "users", "id": team.created_by},
            },
            "updatedBy": {
                "links": {"related": f"{request.host_url}users/{team.updated_by}"},
                "data": {"type": "users", "id": team.updated_by},
            },
            "members": {
                "links": {
                    "self": f"{request.host_url}teams/{team.id}/relationships/members",
                    "related": f"{request.host_url}teams/{team.id}/members",
                },
                "data": [{"type": "users", "id": user.id} for user in team.members],
            },
        },
    }


class UserTeams(Resource):
    @jwt_required
    @call_before([validate_accept_header, validate_uuid])
    @get_resource(User)
    def get(self, user):
        # pylint: disable=no-self-use
        teams = Team.query.filter(Team.members.any(User.id == user.id)).all()
        return {
            "links": {"self": request.url},
            "data": [make_team_resource_object(team) for team in teams],
        }
