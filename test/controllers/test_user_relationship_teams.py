import json
from uuid import uuid4

from flask_jwt_extended import create_access_token
import pytest

from src.db import DB
from src.models import TeamMembership
from .utils import get_content_type

# pylint: disable=invalid-name
pytestmark = [pytest.mark.integration, pytest.mark.controllers]


def test_user_relationship_teams_post_without_auth(client, user1, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` without a token in the
    `Authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        },
    )
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


def test_user_relationship_teams_post_with_invalid_auth(client, user1, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` with an invalid token in
    the `Authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": "abcdefg",
            "Content-Type": "application/vnd.api+json",
        },
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


def test_user_relationship_teams_post_invalid_accept_header(client, user1, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` and the `Accept` header is
    not correctly set
    THEN the response should have a 406 status code and indicate that the `Accept` header is not
    correctly set
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 406
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 406,
                "title": "Not Acceptable",
                "detail": "'Accept' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_user_relationship_teams_post_invalid_content_type_header(client, user1, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` and the `Content-Type`
    header is not correctly set
    THEN the response should have a 415 status code and indicate that the `Content-Type` header is
    not correctly set
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )
    assert response.status_code == 415
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 415,
                "title": "Unsupported Media Type",
                "detail": "'Content-Type' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_user_relationship_teams_post_non_uuid(client, user1, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` but the user ID is not a
    valid UUID
    THEN the response should have a 400 status and indicate that the provided user ID is not a valid
    UUID
    """

    response = client.post(
        "/users/abcdefg/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "User ID abcdefg is not a valid UUID",
            }
        ]
    }


def test_user_relationship_teams_post_nonexistent(client, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` but no user with the given
    ID exists
    THEN the response should have a 404 status and indicate that no user with the given ID exists
    """

    user_id = str(uuid4())
    response = client.post(
        f"/users/{user_id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user_id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 404
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 404,
                "title": "Not Found",
                "detail": f"No User exists with the ID {user_id}",
            }
        ]
    }


def test_user_relationship_teams_post_other_user(client, user1, team1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` but the user ID matches
    a different user than the one that is currently authenticated
    THEN the response should have a 403 status and indicate that the user ID does not match the
    current authenticated user
    """

    user_id = str(uuid4())
    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user_id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 403
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 403,
                "title": "Forbidden",
                "detail": f"User ID {user1.id} does not match the current authenticated user {user_id}",
            }
        ]
    }


@pytest.mark.parametrize(
    "req_body",
    [
        ([{"type": "teams", "id": str(uuid4())}],),
        ({"data": {"type": "teams", "id": str(uuid4())}}),
    ],
)
def test_user_relationship_teams_post_incorrect_structure(client, user1, req_body):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` with an incorrect
    structure for the request body
    THEN the response should have a 400 status and indicate what about the provided body is
    incorrect
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(req_body),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "Invalid request body - must have 'data' property of type 'list'",
            }
        ]
    }


def test_user_relationship_teams_post_varying_semantic_errors(client, user1):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` containing various forms
    of semantic errors
    THEN the response should have a 400 status and indicate what and where the problems are
    """

    team_id = str(uuid4())
    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(
            {
                "data": [
                    str(uuid4()),
                    {"type": "users", "id": user1.id},
                    {"type": "teams", "id": "abc"},
                    {"type": "teams", "id": team_id},
                ]
            }
        ),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "Items of request parameter 'data' must be objects",
                "source": {"pointer": "/data/0",},
            },
            {
                "status": 409,
                "title": "Conflict",
                "detail": "Items of request parameter 'data' must have a 'type' of 'teams'",
                "source": {"pointer": "/data/1/type",},
            },
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "Team ID 'abc' is not a valid UUID",
                "source": {"pointer": "/data/2/id",},
            },
            {
                "status": 404,
                "title": "Not Found",
                "detail": f"No Team exists with the ID '{team_id}'",
                "source": {"pointer": "/data/3",},
            },
        ]
    }


@pytest.mark.parametrize(
    "req_body,expected_status",
    [
        (
            {
                "data": [
                    {"type": "users", "id": str(uuid4())},
                    {"type": "users", "id": str(uuid4())},
                ]
            },
            409,
        ),
        (
            {
                "data": [
                    {"type": "teams", "id": str(uuid4())},
                    {"type": "teams", "id": str(uuid4())},
                ]
            },
            404,
        ),
    ],
)
def test_user_relationship_teams_post_same_semantic_errors_status(
    client, user1, req_body, expected_status
):
    """
    WHEN a post request is made to `/users/<user_id>/relationships/teams` containing one or more
    instances of a single form of semantic error
    THEN the response should have a status corresponding to that type of semantic error
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(req_body),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == expected_status


def test_user_relationship_teams_post_success(client, user1, team1):
    """
    GIVEN a user exists on the platform
    WHEN a post request is made to `/users/<user_id>/relationships/teams` with that user's ID
    THEN the response should have a 201 status and return the resource identifiers for the teams
    that were added
    """

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 201
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {
            "self": f"http://localhost/users/{user1.id}/relationships/teams",
            "related": f"http://localhost/users/{user1.id}/teams",
        },
        "data": [{"type": "teams", "id": team1.id}],
    }


def test_user_relationship_teams_post_some_duplicates(client, user1, team1, team2):
    """
    GIVEN an existing user and team, with the user being a member of that team
    WHEN a post request is made to `/users/<user_id>/relationships/teams` that contains the
    existing relationship in addition to new relationships
    THEN the response should have a 201 status and return the resource identifiers for the
    relationships that were created, omitting the duplicates
    """

    DB.session.add(
        TeamMembership(
            user_id=user1.id, team_id=team2.id, created_by=user1.id, updated_by=user1.id
        )
    )
    DB.session.commit()

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(
            {
                "data": [
                    {"type": "teams", "id": team1.id},
                    {"type": "teams", "id": team2.id},
                ]
            }
        ),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 201
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "links": {
            "self": f"http://localhost/users/{user1.id}/relationships/teams",
            "related": f"http://localhost/users/{user1.id}/teams",
        },
        "data": [{"type": "teams", "id": team1.id}],
    }


def test_user_relationship_teams_post_all_duplicates(client, user1, team1):
    """
    GIVEN an existing user and team, with the user being a member of that team
    WHEN a post request is made to `/users/<user_id>/relationships/teams` that contains only the
    existing relationship
    THEN the response should have a 204 Status and return no content
    """

    DB.session.add(
        TeamMembership(
            user_id=user1.id, team_id=team1.id, created_by=user1.id, updated_by=user1.id
        )
    )
    DB.session.commit()

    response = client.post(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id},]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 204
    assert get_content_type(response) == "application/vnd.api+json"
    assert len(response.data.decode()) == 0


def test_user_relationship_teams_delete_without_auth(client, user1, team1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` without a token in the
    `Authorization` header
    THEN the response should have a 401 status code and indicate that the header is missing
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        },
    )
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


def test_user_relationship_teams_delete_with_invalid_auth(client, user1, team1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` with an invalid token in
    the `Authorization` header
    THEN the response should have a 422 status code and indicate that the authorization header is
    malformed
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": "abcdefg",
            "Content-Type": "application/vnd.api+json",
        },
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


def test_user_relationship_teams_delete_invalid_accept_header(client, user1, team1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` and the `Accept` header
    is not correctly set
    THEN the response should have a 406 status code and indicate that the `Accept` header is not
    correctly set
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 406
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 406,
                "title": "Not Acceptable",
                "detail": "'Accept' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_user_relationship_teams_delete_invalid_content_type_header(
    client, user1, team1
):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` and the `Content-Type`
    header is not correctly set
    THEN the response should have a 415 status code and indicate that the `Content-Type` header is
    not correctly set
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
        },
    )
    assert response.status_code == 415
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 415,
                "title": "Unsupported Media Type",
                "detail": "'Content-Type' header must be set to 'application/vnd.api+json'",
            }
        ]
    }


def test_user_relationship_teams_delete_non_uuid(client, user1, team1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` but the user ID is not a
    valid UUID
    THEN the response should have a 400 status and indicate that the provided user ID is not a valid
    UUID
    """

    response = client.delete(
        "/users/abcdefg/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "User ID abcdefg is not a valid UUID",
            }
        ]
    }


def test_user_relationship_teams_delete_nonexistent(client, team1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` but no user with the
    given ID exists
    THEN the response should have a 404 status and indicate that no user with the given ID exists
    """

    user_id = str(uuid4())
    response = client.delete(
        f"/users/{user_id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user_id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 404
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 404,
                "title": "Not Found",
                "detail": f"No User exists with the ID {user_id}",
            }
        ]
    }


def test_user_relationship_teams_delete_other_user(client, user1, team1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` but the user ID matches
    a different user than the one that is currently authenticated
    THEN the response should have a 403 status and indicate that the user ID does not match the
    current authenticated user
    """

    user_id = str(uuid4())
    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user_id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 403
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 403,
                "title": "Forbidden",
                "detail": f"User ID {user1.id} does not match the current authenticated user {user_id}",
            }
        ]
    }


@pytest.mark.parametrize(
    "req_body",
    [
        ([{"type": "teams", "id": str(uuid4())}],),
        ({"data": {"type": "teams", "id": str(uuid4())}}),
    ],
)
def test_user_relationship_teams_delete_incorrect_structure(client, user1, req_body):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` with an incorrect
    structure for the request body
    THEN the response should have a 400 status and indicate what about the provided body is
    incorrect
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(req_body),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "Invalid request body - must have 'data' property of type 'list'",
            }
        ]
    }


def test_user_relationship_teams_delete_varying_semantic_errors(client, user1):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` containing various forms
    of semantic errors
    THEN the response should have a 400 status and indicate what and where the problems are
    """

    team_id = str(uuid4())
    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(
            {
                "data": [
                    str(uuid4()),
                    {"type": "users", "id": user1.id},
                    {"type": "teams", "id": "abc"},
                    {"type": "teams", "id": team_id},
                ]
            }
        ),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == 400
    assert get_content_type(response) == "application/vnd.api+json"
    assert json.loads(response.data.decode()) == {
        "errors": [
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "Items of request parameter 'data' must be objects",
                "source": {"pointer": "/data/0",},
            },
            {
                "status": 409,
                "title": "Conflict",
                "detail": "Items of request parameter 'data' must have a 'type' of 'teams'",
                "source": {"pointer": "/data/1/type",},
            },
            {
                "status": 400,
                "title": "Bad Request",
                "detail": "Team ID 'abc' is not a valid UUID",
                "source": {"pointer": "/data/2/id",},
            },
            {
                "status": 404,
                "title": "Not Found",
                "detail": f"No Team exists with the ID '{team_id}'",
                "source": {"pointer": "/data/3",},
            },
        ]
    }


@pytest.mark.parametrize(
    "req_body,expected_status",
    [
        (
            {
                "data": [
                    {"type": "users", "id": str(uuid4())},
                    {"type": "users", "id": str(uuid4())},
                ]
            },
            409,
        ),
        (
            {
                "data": [
                    {"type": "teams", "id": str(uuid4())},
                    {"type": "teams", "id": str(uuid4())},
                ]
            },
            404,
        ),
    ],
)
def test_user_relationship_teams_delete_same_semantic_errors_status(
    client, user1, req_body, expected_status
):
    """
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` containing one or more
    instances of a single form of semantic error
    THEN the response should have a status corresponding to that type of semantic error
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps(req_body),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )
    assert response.status_code == expected_status


def test_user_relationship_teams_delete_success(client, user1, team1):
    """
    GIVEN a user exists on the platform and is a member of a team
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` with that user's ID
    THEN the response should have a 204 status and return no content
    """

    DB.session.add(
        TeamMembership(
            user_id=user1.id, team_id=team1.id, created_by=user1.id, updated_by=user1.id
        )
    )
    DB.session.commit()

    assert team1 in user1.teams

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )

    assert team1 not in user1.teams
    assert response.status_code == 204
    assert get_content_type(response) == "application/vnd.api+json"
    assert len(response.data.decode()) == 0


def test_user_relationship_teams_delete_nonexistent_relationship(client, user1, team1):
    """
    GIVEN a user exists on the platform
    WHEN a delete request is made to `/users/<user_id>/relationships/teams` to remove them from a
    team they are not a member of
    THEN the response should have a 204 status and return no content
    """

    response = client.delete(
        f"/users/{user1.id}/relationships/teams",
        data=json.dumps({"data": [{"type": "teams", "id": team1.id}]}),
        headers={
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {create_access_token(identity=user1.id)}",
            "Content-Type": "application/vnd.api+json",
        },
    )

    assert response.status_code == 204
    assert get_content_type(response) == "application/vnd.api+json"
    assert len(response.data.decode()) == 0
