from flask import request

from ..exceptions import NotAcceptableError, UnsupportedMediaTypeError


def validate_accept_header(*args, **kwargs):
    if request.headers.get("Accept") != "application/vnd.api+json":
        raise NotAcceptableError(
            "'Accept' header must be set to 'application/vnd.api+json'"
        )


def validate_content_type_header(*args, **kwargs):
    if request.headers.get("Content-Type") != "application/vnd.api+json":
        raise UnsupportedMediaTypeError(
            "'Content-Type' header must be set to 'application/vnd.api+json'"
        )
