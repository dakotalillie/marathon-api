def make_error_response(error):
    return dict(errors=[error.to_dict()]), error.status


class ClientError(Exception):
    status = -1
    default_message = ""
    default_title = ""

    def __init__(self, message=None, title=None):
        super().__init__()
        self.message = message if message else self.__class__.default_message
        self.title = title if title else self.__class__.default_title

    def to_dict(self):
        return dict(title=self.title, status=self.__class__.status, detail=self.message)


class BadRequestError(ClientError):
    status = 400
    default_title = "Bad Request"
    default_message = "The requested operation could not be completed"


class UnauthorizedError(ClientError):
    status = 401
    default_title = "Unauthorized"
    default_message = (
        "The requested operation could not be completed due to missing or invalid"
        "authorization"
    )


class ForbiddenError(ClientError):
    status = 403
    default_title = "Forbidden"
    default_message = "The requested operation is forbidden"


class NotFoundError(ClientError):
    status = 404
    default_title = "Not Found"
    default_message = "The requested resource does not exist"


class ConflictError(ClientError):
    status = 409
    default_title = "Conflict"
    default_message = "The requested operation could not be completed due to a conflict"


class UnprocessableEntityError(ClientError):
    status = 422
    default_title = "Unprocessable Entity"
    default_message = (
        "The requested operation could not be completed due to semantic errors"
    )
