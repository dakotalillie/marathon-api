from flask_restful import fields

from .common import COMMON_FIELDS


class TeamMarshaller:
    """
    A class which determines how the data from the Team model should be marshalled
    """

    __fields = dict(**COMMON_FIELDS, name=fields.String)

    @classmethod
    def all(cls):
        return cls.__fields
