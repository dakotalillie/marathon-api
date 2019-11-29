import json
from uuid import uuid4

from flask_jwt_extended import create_access_token

from src.db import DB
from src.models import TeamMembership
from src.exceptions import BadRequestError, ForbiddenError, NotFoundError
from .utils import get_content_type


def test_team_memberships_detail_delete_without_auth(client):
    """
    WHEN a delete request is made to `/team_memberships/<team_membership_id>` without a token in the
    `authorization` header
    THEN the response should have a 401 status code and indicate that the authorization header is
    missing
    """

    response = client.delete(f"/team_memberships/{str(uuid4())}")
    assert response.status_code == 401
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 401,
                "title": "Unauthorized",
                "detail": "Missing Authorization Header",
            }
        ]
    }


def test_team_memberships_detail_delete_with_invalid_auth(client):
    """
    WHEN a delete request is made to `/team_memberships/<team_membership_id>` with an invalid token
    in the `authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.delete(
        f"/team_memberships/{str(uuid4())}", headers=dict(authorization="abcdefg")
    )
    assert response.status_code == 422
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 422,
                "title": "Unprocessable Entity",
                "detail": "Bad Authorization header. Expected value 'Bearer <JWT>'",
            }
        ]
    }


def test_team_memberships_detail_delete_non_uuid(client):
    """
    WHEN a delete request is made to `/team_memberships/<team_membership_id>` but the team
    membership ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided team membership ID is
    not a UUID
    """

    response = client.delete(
        f"/team_memberships/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[
            BadRequestError("TeamMembership ID abcdefg is not a valid UUID").to_dict()
        ]
    )


def test_team_membership_detail_delete_nonexistent(client):
    """
    WHEN a delete request is made to `/team_memberships/<team_membership_id>` but no team membership
    with the given ID exists
    THEN the response should have a 404 status and indicate that no team membership with the given
    ID exists
    """

    team_membership_id = str(uuid4())
    response = client.delete(
        f"/team_memberships/{team_membership_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid4()))}"
        ),
    )

    assert response.status_code == 404
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[
            NotFoundError(
                f"No TeamMembership exists with the ID {team_membership_id}"
            ).to_dict()
        ]
    )


def test_team_membership_detail_delete_non_member(client, user1, user2, team1):
    """
    GIVEN an existing team membership
    WHEN a delete request is made to `/team_memberships/<team_membership_id>` to delete the
    membership, but the authenticated user is not a member of the team the membership is for
    THEN the response should have a 403 status and indicate that the authenticated user must be a
    member of the team to perform this operation
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    team_membership = TeamMembership.query.filter_by(
        team_id=team1.id, user_id=user1.id
    ).first()

    response = client.delete(
        f"/team_memberships/{team_membership.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user2.id)}"),
    )

    assert response.status_code == 403
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == dict(
        errors=[
            ForbiddenError(
                f"User {user2.id} does not have permission to modify TeamMembership "
                f"{team_membership.id} because they are not a member of Team {team1.id}"
            ).to_dict()
        ]
    )


def test_team_membership_detail_delete_success(client, user1, team1):
    """
    GIVEN an existing team membership
    WHEN a delete request is made to `team_memberships/<team_membership_id` with the team
    membership's ID
    THEN the team membership should be removed from the database and the response should have a
    204 status code
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    team_membership = TeamMembership.query.filter_by(
        team_id=team1.id, user_id=user1.id
    ).first()

    assert user1 in team1.members

    response = client.delete(
        f"/team_memberships/{team_membership.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )

    assert response.status_code == 204
    assert get_content_type(response) == "application/vnd.api+json"
    assert user1 not in team1.members
    assert len(response.data) == 0
