"""
Decorators which can be used to wrap controller methods in order to provide
common functionality.
"""

import functools

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
