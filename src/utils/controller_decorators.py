"""
Decorators which can be used to wrap controller methods in order to provide
common functionality.
"""

import functools

from flask import request
from flask_restful import marshal

from .string_transformations import camel_to_snake
from ..exceptions import NotFoundError


def call_before(callbacks):
    """
    Calls a series of callbacks before calling the wrapped function. Commonly
    used for performing a series of validation checks before invoking the
    primary controller logic.

    Note that because calling the functions with both *args and **kwargs can
    lead to function parameters being defined twice, only kwargs are passed
    in to the callbacks.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for callback in callbacks:
                callback(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_resource(model):
    """
    Retrieves an individual resource by it's ID, raising a NotFoundError if no
    such resource exists. This is intended as a convenient wrapper for resource
    detail controller methods, which commonly need to perform this operation.
    """

    model_name = model.__name__
    snake_case_model_name = camel_to_snake(model_name)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            resource_id = kwargs[f"{snake_case_model_name}_id"]
            resource = model.query.filter_by(id=resource_id).first()
            if not resource:
                raise NotFoundError(f"No {model_name} exists with the ID {resource_id}")
            return func(*args, **dict(zip((snake_case_model_name,), (resource,))))

        return wrapper

    return decorator


def format_response(config):
    """
    Formats the resource(s) returned by a controller into a structure compliant with the JSON API
    specification. More information on the JSON API standard can be found at https://jsonapi.org/

    Parameters
    ----------
    config (dict): a configuration dict which allows for customization of the data included in the
    response. A configuration MUST have the following propties:

    - name (str) the name of the resource
    - marshaller (Marshaller) the marshaller which determines which of the resource's properties
      will be included

    A top-level configuration MAY have the following properties:

    - relationships(Config[]) an array of configuration dicts for resources which are related to
      the primary resource.

    Configuration objects contained within the "relationships" array MAY have the following
    properties:

    - related_name (name) the name of the resource as it relates to the primary resource, to be used
      in cases where this differs from the ordinary name of the resource. For instance, a Team may
      include Users, but it may access them as team.members instead of team.users.

    Example
    -------
    @format_response(
        {
            "name": "teams",
            "marshaller": TeamMarshaller.omit("id"),
            "relationships": [
                {
                    "name": "team_memberships",
                    "marshaller": TeamMembershipMarshaller.pick("user_id", "team_id"),
                },
                {
                    "related_name": "members",
                    "name": "users",
                    "marshaller": UserMarshaller.pick("name"),
                },
            ],
        }
    )
    def get(self):
        return Team.query.all()
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            formatted_body = _get_formatted_response_body(response, config)
            status_code = response[1] if isinstance(response, tuple) else 200
            return formatted_body, status_code

        return wrapper

    return decorator


def _get_formatted_response_body(response, config):
    resource_or_resource_list = _get_resource_or_resource_list(response)
    return {
        "links": {"self": request.url},
        "data": _make_data(resource_or_resource_list, config),
        **(
            {"included": _make_included(resource_or_resource_list, config)}
            if "relationships" in config
            else {}
        ),
    }


def _get_resource_or_resource_list(response):
    if isinstance(response, tuple):
        return response[0]
    return response


def _make_data(resource_or_resource_list, config):
    return (
        [
            _make_resource_object(resource, config)
            for resource in resource_or_resource_list
        ]
        if isinstance(resource_or_resource_list, list)
        else _make_resource_object(resource_or_resource_list, config)
    )


def _make_resource_object(resource, config):
    return {
        "type": config["name"],
        "id": resource.id,
        "attributes": marshal(resource, config["marshaller"]),
        "links": {"self": f"{request.host_url}{config['name']}/{resource.id}"},
        **(_make_relationships(resource, config) if "relationships" in config else {}),
    }


def _make_relationships(resource, config):
    relationships = [
        _make_individual_relationship(resource, nested_config)
        for nested_config in config["relationships"]
    ]
    return {"relationships": dict(i for r in relationships for i in r.items())}


def _make_individual_relationship(resource, config):
    return {
        _get_related_name(config): {
            "data": [
                _make_id_resource_object(related_resource, config)
                for related_resource in getattr(resource, _get_related_name(config))
            ]
        }
    }


def _get_related_name(config):
    return config.get("related_name", config["name"])


def _make_id_resource_object(resource, config):
    return {"type": config["name"], "id": resource.id}


def _make_included(resource_or_resource_list, config):
    return [
        _make_resource_object(related_resource, relationship)
        for relationship in config["relationships"]
        for resource in (
            resource_or_resource_list
            if isinstance(resource_or_resource_list, list)
            else [resource_or_resource_list]
        )
        for related_resource in getattr(resource, _get_related_name(relationship))
    ]
