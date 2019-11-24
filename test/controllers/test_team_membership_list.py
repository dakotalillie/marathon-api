from functools import partial
import json
from uuid import uuid4

from flask_jwt_extended import create_access_token
import pytest

from src.db import DB
from src.exceptions import BadRequestError
from src.models import TeamMembership


def get_existing_team_memberships(user_id, team_id):
    return TeamMembership.query.filter_by(user_id=user_id, team_id=team_id)


def test_team_memberships_list_post_without_auth(client):
    """
    WHEN a post request is made to `/team_memberships` without a token in the `authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.post(
        "/team_memberships", data=dict(user=str(uuid4()), team=str(uuid4()))
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


def test_team_memberships_list_post_with_invalid_auth(client):
    """
    WHEN a post request is made to `/team_memberships` with an invalid token in the `authorization`
    header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.post(
        "/team_memberships",
        data=dict(user=str(uuid4()), team=str(uuid4())),
        headers=dict(authorization="abcdefg"),
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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            dict(),
            dict(
                user="Missing required parameter in the post body",
                team="Missing required parameter in the post body",
            ),
        ),
        (
            dict(user="username"),
            dict(team="Missing required parameter in the post body"),
        ),
        (
            dict(team="password"),
            dict(user="Missing required parameter in the post body"),
        ),
    ],
)
def test_team_memberships_list_post_missing_parameters(client, test_input, expected):
    """
    WHEN a post request is made to `/team_memberships` which is missing required fields
    THEN the response should have a 400 status code and indicate which fields are missing
    """

    response = client.post(
        "/team_memberships",
        data=test_input,
        headers=dict(
            authorization=f"Bearer {create_access_token(identity=str(uuid4()))}"
        ),
    )
    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(message=expected)


def test_team_memberships_list_post_non_existent_user(client, team1):
    """
    WHEN a post request is made to `/team_memberships` for a non-existent user
    THEN the response should have a 400 status code and indicate that the user does not exist
    """

    user_id = str(uuid4())
    response = client.post(
        "/team_memberships",
        data=dict(user=user_id, team=team1.id),
        headers=dict(authorization=f"Bearer {create_access_token(identity=user_id)}"),
    )

    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[
            BadRequestError(
                f"Cannot complete operation because user {user_id} does not exist"
            ).to_dict()
        ]
    )


def test_team_memberships_list_post_non_existent_team(client, user1):
    """
    WHEN a post request is made to `/team_memberships` for a non-existent team
    THEN the response should have a 400 status code and indicate that the team does not exist
    """

    team_id = str(uuid4())
    response = client.post(
        "/team_memberships",
        data=dict(user=user1.id, team=team_id),
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )

    assert response.status_code == 400
    assert json.loads(response.data.decode()) == dict(
        errors=[
            BadRequestError(
                f"Cannot complete operation because team {team_id} does not exist"
            ).to_dict()
        ]
    )


def test_team_memberships_list_post_duplicate_member(client, user1, team1):
    """
    GIVEN an existing team and user, with the user being a member of the team
    WHEN a post request is made to `/team_memberships` for the same team and user
    THEN the response should have a 204 status code and the modification should be ignored
    """

    get_team_members = partial(get_existing_team_memberships, user1.id, team1.id)
    team1.members.append(user1)
    DB.session.add(team1)
    DB.session.commit()

    original_updated_at = get_team_members().first().updated_at

    response = client.post(
        "/team_memberships",
        data=dict(user=user1.id, team=team1.id),
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )

    assert response.status_code == 204
    assert get_team_members().count() == 1
    assert get_team_members().first().updated_at == original_updated_at
    assert len(response.data) == 0


def test_team_memberships_list_post_success(client, user1, team1):
    """
    GIVEN an existing team and user, with the user not being a member of the team
    WHEN a post request is made to `/team_memberships` for the given team and user
    THEN the response should have a 201 status code and the user should be added to the team
    """

    get_team_members = partial(get_existing_team_memberships, user1.id, team1.id)
    assert get_team_members().count() == 0

    response = client.post(
        "/team_memberships",
        data=dict(user=user1.id, team=team1.id),
        headers=dict(authorization=f"Bearer {create_access_token(identity=user1.id)}"),
    )

    assert response.status_code == 201
    assert get_team_members().count() == 1
    assert len(response.data) == 0
