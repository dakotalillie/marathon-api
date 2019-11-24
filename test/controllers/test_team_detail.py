import json
import uuid

from flask_jwt_extended import create_access_token
import pytest

from src.db import DB
from src.exceptions import BadRequestError, ForbiddenError, NotFoundError
from src.models import Team

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.integration,
    pytest.mark.controllers,
]


def test_team_detail_get_without_auth(client):
    """
    WHEN a get request is made to to `/teams/<team_id>` without a token in the `authorization`
    header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.get(f"/teams/{str(uuid.uuid4())}")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 401,
                "title": "Unauthorized",
                "detail": "Missing Authorization Header",
            }
        ]
    }


def test_team_detail_get_with_invalid_auth(client):
    """
    WHEN a get request is made to `/teams/<team_id>` with an invalid token in the `authorization`
    header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.get(
        f"/teams/{str(uuid.uuid4())}", headers=dict(authorization="abcdefg")
    )
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 422,
                "title": "Unprocessable Entity",
                "detail": "Bad Authorization header. Expected value 'Bearer <JWT>'",
            }
        ]
    }


def test_team_detail_get_non_uuid(client):
    """
    WHEN a get request is made to `/teams/<team_id>` but the team ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided team ID is not a valid
    UUID
    """

    response = client.get(
        "/teams/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError("Team ID abcdefg is not a valid UUID").to_dict()]
    )


def test_team_detail_get_nonexistent(client):
    """
    WHEN a get request is made to `/teams/<team_id>` but no team with the given ID exists
    THEN the response should have a 404 status and indicate that no team with the given ID exists
    """

    team_id = str(uuid.uuid4())
    response = client.get(
        f"/teams/{team_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[NotFoundError(f"No Team exists with the ID {team_id}").to_dict()]
    )


def test_team_detail_get_success(client, team1, user1):
    """
    GIVEN an existing team on the platform
    WHEN a get request is made to `/teams/<team_id>` with the team's ID
    THEN the response should have a 200 status code and return the details of the team
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    response = client.get(
        f"/teams/{team1.id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    team_membership = team1.team_memberships[0]
    assert response.status_code == 200
    assert json.loads(response.data.decode()) == {
        "links": {"self": f"http://localhost/teams/{team1.id}"},
        "data": {
            "type": "teams",
            "id": team1.id,
            "attributes": {
                "created_at": team1.created_at.isoformat(),
                "updated_at": team1.updated_at.isoformat(),
                "is_active": True,
                "name": team1.name,
            },
            "relationships": {
                "team_memberships": {
                    "data": [{"type": "team_memberships", "id": team_membership.id}]
                },
                "members": {"data": [{"type": "users", "id": user1.id}]},
            },
            "links": {"self": f"http://localhost/teams/{team1.id}"},
        },
        "included": [
            {
                "type": "team_memberships",
                "id": team_membership.id,
                "attributes": {
                    "user_id": user1.id,
                    "team_id": team1.id,
                    "created_at": team_membership.created_at.isoformat(),
                    "updated_at": team_membership.updated_at.isoformat(),
                    "is_active": True,
                },
                "links": {
                    "self": f"http://localhost/team_memberships/{team_membership.id}"
                },
            },
            {
                "type": "users",
                "id": user1.id,
                "attributes": {
                    "created_at": user1.created_at.isoformat(),
                    "updated_at": user1.updated_at.isoformat(),
                    "is_active": True,
                    "first_name": user1.first_name,
                    "last_name": user1.last_name,
                    "username": user1.username,
                    "email": user1.email,
                    "visibility": user1.visibility,
                },
                "links": {"self": f"http://localhost/users/{user1.id}"},
            },
        ],
    }


def test_team_detail_patch_without_auth(client):
    """
    WHEN a patch request is made to `/teams/<team_id>` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.patch(
        f"/teams/{str(uuid.uuid4())}", data=dict(name="new team name")
    )
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 401,
                "title": "Unauthorized",
                "detail": "Missing Authorization Header",
            }
        ]
    }


def test_team_detail_patch_with_invalid_auth(client):
    """
    WHEN a patch request is made to `/teams/<team_id>` with an invalid token in the `authorization`
    header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.patch(
        f"/teams/{str(uuid.uuid4())}",
        headers=dict(authorization="abcdefg"),
        data=dict(name="new team name"),
    )
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 422,
                "title": "Unprocessable Entity",
                "detail": "Bad Authorization header. Expected value 'Bearer <JWT>'",
            }
        ]
    }


def test_team_detail_patch_non_uuid(client):
    """
    WHEN a patch request is made to `/teams/<team_id>` but the team ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided team ID is not a valid
    UUID
    """

    response = client.patch(
        "/teams/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
        data=dict(name="new team name"),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError("Team ID abcdefg is not a valid UUID").to_dict()]
    )


def test_team_detail_patch_nonexistent(client):
    """
    WHEN a patch request is made to `/teams/<team_id>` but no team with the given ID exists
    THEN the response should have a 404 status and indicate that no team with the given ID exists
    """

    team_id = str(uuid.uuid4())
    response = client.patch(
        f"/teams/{team_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
        data=dict(name="new team name"),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[NotFoundError(f"No Team exists with the ID {team_id}").to_dict()]
    )


def test_team_detail_patch_not_team_member(client, user1, team1):
    """
    GIVEN an existing user and team
    WHEN a patch request is made to `/teams/<team_id>` but the authenticated user is not a member of
    the team being edited
    THEN the response should have a 403 status and indicate that the operation is forbidden because
    the user is not a member of the team
    """

    response = client.patch(
        f"/teams/{team1.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
        data=dict(name="new team name"),
    )
    assert response.status_code == 403
    assert json.loads(response.data.decode()) == dict(
        errors=[
            ForbiddenError(
                f"User {user1.id} cannot modify team {team1.id} because they are not a member"
            ).to_dict()
        ]
    )


def test_team_detail_patch_success(client, user1, team1):
    """
    GIVEN an existing user and team, with the authenticated user being a member of that team
    WHEN a patch request is made to `/teams/<team_id>`
    THEN the response should have a 200 status and return the updated details of the team
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    response = client.patch(
        f"/teams/{team1.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
        data=dict(name="new team name"),
    )
    assert response.status_code == 200
    assert Team.query.filter_by(id=team1.id).first().name == "new team name"
    assert json.loads(response.data.decode()) == {
        "links": {"self": f"http://localhost/teams/{team1.id}"},
        "data": {
            "type": "teams",
            "id": team1.id,
            "attributes": {
                "created_at": team1.created_at.isoformat(),
                "updated_at": team1.updated_at.isoformat(),
                "is_active": True,
                "name": "new team name",
            },
            "links": {"self": f"http://localhost/teams/{team1.id}"},
        },
    }


def test_team_detail_delete_without_auth(client):
    """
    WHEN a delete request is made to `/teams/<team_id>` without a token in the `authorization`
    header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.delete(f"/teams/{str(uuid.uuid4())}")
    assert response.status_code == 401
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 401,
                "title": "Unauthorized",
                "detail": "Missing Authorization Header",
            }
        ]
    }


def test_team_detail_delete_with_invalid_auth(client):
    """
    WHEN a delete request is made to `/teams/<team_id>` with an invalid token in the `authorization`
    header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.delete(
        f"/teams/{str(uuid.uuid4())}", headers=dict(authorization="abcdefg"),
    )
    assert response.status_code == 422
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 422,
                "title": "Unprocessable Entity",
                "detail": "Bad Authorization header. Expected value 'Bearer <JWT>'",
            }
        ]
    }


def test_team_detail_delete_non_uuid(client):
    """
    WHEN a delete request is made to `/teams/<team_id>` but the team ID is not a valid UUID
    THEN the response should have a 400 status and indicate that the provided team ID is not a valid
    UUID
    """

    response = client.delete(
        "/teams/abcdefg",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[BadRequestError("Team ID abcdefg is not a valid UUID").to_dict()]
    )


def test_team_detail_delete_nonexistent(client):
    """
    WHEN a delete request is made to `/teams/<team_id>` but no team with the given ID exists
    THEN the response should have a 404 status and indicate that no team with the given ID exists
    """

    team_id = str(uuid.uuid4())
    response = client.delete(
        f"/teams/{team_id}",
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid.uuid4()))}"
        ),
    )
    assert response.status_code == 404
    assert json.loads(response.data.decode()) == dict(
        errors=[NotFoundError(f"No Team exists with the ID {team_id}").to_dict()]
    )


def test_team_detail_delete_not_team_member(client, user1, team1):
    """
    GIVEN an existing user and team
    WHEN a delete request is made to `/teams/<team_id>` but the authenticated user is not a member
    of the team being edited
    THEN the response should have a 403 status and indicate that the operation is forbidden because
    the user is not a member of the team
    """

    response = client.delete(
        f"/teams/{team1.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )
    assert response.status_code == 403
    assert json.loads(response.data.decode()) == dict(
        errors=[
            ForbiddenError(
                f"User {user1.id} cannot modify team {team1.id} because they are not a member"
            ).to_dict()
        ]
    )


def test_team_detail_delete_success(client, user1, team1):
    """
    GIVEN an existing user and team, with the authenticated user being a member of that team
    WHEN a delete request is made to `/teams/<team_id>`
    THEN the team should be removed from the database and the response should have a 204 status
    """

    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    response = client.delete(
        f"/teams/{team1.id}",
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )
    assert response.status_code == 204
    assert Team.query.filter_by(id=team1.id).first() is None
    assert len(response.data) == 0
