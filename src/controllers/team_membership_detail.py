from flask import Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..db import DB
from ..exceptions import BadRequestError, ForbiddenError
from ..models import Team, TeamMembership, User
from ..utils.controller_decorators import call_before, get_resource
from ..utils.is_valid_uuid import is_valid_uuid


def validate_uuid(*args, team_membership_id):
    if not is_valid_uuid(team_membership_id):
        raise BadRequestError(
            f"TeamMembership ID {team_membership_id} is not a valid UUID"
        )


def validate_permissions(*args, team_membership):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(id=current_user_id).first()
    team = Team.query.filter_by(id=team_membership.team_id).first()
    if (not current_user) or (current_user not in team.members):
        raise ForbiddenError(
            f"User {current_user_id} does not have permission to modify TeamMembership "
            f"{team_membership.id} because they are not a member of Team {team.id}"
        )


class TeamMembershipDetail(Resource):
    @jwt_required
    @call_before([validate_uuid])
    @get_resource(TeamMembership)
    @call_before([validate_permissions])
    def delete(self, team_membership):
        # pylint: disable=no-self-use
        DB.session.delete(team_membership)
        DB.session.commit()
        return Response(status=204)
