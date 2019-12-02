from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from ..db import DB
from ..exceptions import BadRequestError, ConflictError, NotFoundError, ForbiddenError
from ..models import User, Team
from ..utils.controller_decorators import call_before, get_resource
from ..utils.controller_validators import (
    validate_accept_header,
    validate_content_type_header,
)
from ..utils.is_valid_uuid import is_valid_uuid


def validate_user_uuid(*args, user_id):
    if not is_valid_uuid(user_id):
        raise BadRequestError(f"User ID {user_id} is not a valid UUID")


def validate_is_current_user(*args, user_id):
    authenticated_user_id = get_jwt_identity()
    if authenticated_user_id != user_id:
        raise ForbiddenError(
            f"User ID {user_id} does not match the current authenticated user {authenticated_user_id}",
        )


def validate_request_structure(*args, **kwargs):
    if ("data" not in request.json) or (not isinstance(request.json["data"], list)):
        raise BadRequestError(
            "Invalid request body - must have 'data' property of type 'list'"
        )


def validate_is_object(relationship_object, index):
    if not isinstance(relationship_object, dict):
        raise BadRequestError(
            "Items of request parameter 'data' must be objects",
            source={"pointer": f"/data/{index}"},
        )


def validate_type_is_teams(relationship_object, index):
    if relationship_object.get("type") != "teams":
        raise ConflictError(
            "Items of request parameter 'data' must have a 'type' of 'teams'",
            source={"pointer": f"/data/{index}/type"},
        )


def validate_team_uuid_is_valid_uuid(team_id, index):
    if not is_valid_uuid(team_id):
        raise BadRequestError(
            f"Team ID '{team_id}' is not a valid UUID",
            source={"pointer": f"/data/{index}/id"},
        )


def validate_team_exists(team, team_id, index):
    if not team:
        raise NotFoundError(
            f"No Team exists with the ID '{team_id}'",
            source={"pointer": f"/data/{index}"},
        )


def get_team(relationship_object, index):
    validate_is_object(relationship_object, index)
    validate_type_is_teams(relationship_object, index)
    team_id = relationship_object.get("id")
    validate_team_uuid_is_valid_uuid(team_id, index)
    team = Team.query.filter_by(id=team_id).first()
    validate_team_exists(team, team_id, index)
    return team


def get_teams_and_errors():
    teams = []
    errors = []
    for index, relationship_object in enumerate(request.json["data"]):
        try:
            teams.append(get_team(relationship_object, index))
        except (BadRequestError, ConflictError, NotFoundError) as error:
            errors.append(error)
    return teams, errors


def make_error_response(errors):
    status = (
        errors[0].status
        if all(True for e in errors if e.status == errors[0].status)
        else 400
    )
    return {"errors": [error.to_dict() for error in errors]}, status


class UserRelationshipTeams(Resource):
    @jwt_required
    @call_before(
        [
            validate_accept_header,
            validate_content_type_header,
            validate_user_uuid,
            validate_is_current_user,
            validate_request_structure,
        ]
    )
    @get_resource(User)
    def post(self, user):
        # pylint: disable=no-self-use
        teams, errors = get_teams_and_errors()
        if len(errors) > 0:
            return make_error_response(errors)
        teams_to_add = [team for team in teams if team not in user.teams]
        if len(teams_to_add) == 0:
            return None, 204
        for team in teams_to_add:
            user.teams.append(team)
        DB.session.add(user)
        DB.session.commit()
        return (
            {
                "links": {
                    "self": f"{request.host_url}users/{user.id}/relationships/teams",
                    "related": f"{request.host_url}users/{user.id}/teams",
                },
                "data": [{"type": "teams", "id": team.id} for team in teams_to_add],
            },
            201,
        )

    @jwt_required
    @call_before(
        [
            validate_accept_header,
            validate_content_type_header,
            validate_user_uuid,
            validate_is_current_user,
            validate_request_structure,
        ]
    )
    @get_resource(User)
    def delete(self, user):
        # pylint: disable=no-self-use
        teams, errors = get_teams_and_errors()
        if len(errors) > 0:
            return make_error_response(errors)
        for team in teams:
            if team in user.teams:
                user.teams.remove(team)
        DB.session.add(user)
        DB.session.commit()
        return None, 204
