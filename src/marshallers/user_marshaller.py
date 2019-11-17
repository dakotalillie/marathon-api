from flask_restful import fields

from .common import COMMON_FIELDS


class UserMarshaller:
    """
    A class which determines how the data from the User model should be marshalled
    """

    __fields = dict(
        **COMMON_FIELDS,
        first_name=fields.String,
        last_name=fields.String,
        username=fields.String,
        email=fields.String,
        visibility=fields.String,
    )

    @classmethod
    def all(cls):
        return cls.__fields
