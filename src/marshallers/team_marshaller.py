from flask_restful import fields


class TeamMarshaller:
    """
    A class which determines how the data from the Team model should be marshalled
    """

    __fields = dict(
        id=fields.String,
        name=fields.String,
        created_at=fields.DateTime(dt_format="iso8601"),
        updated_at=fields.DateTime(dt_format="iso8601"),
        is_active=fields.Boolean,
    )

    @classmethod
    def all(cls):
        return cls.__fields

