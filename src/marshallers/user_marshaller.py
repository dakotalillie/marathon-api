from flask_restful import fields


class UserMarshaller:
    """
    A class which determines how the data from the User model should be marshalled
    """

    __fields = dict(
        id=fields.String,
        first_name=fields.String,
        last_name=fields.String,
        username=fields.String,
        email=fields.String,
        visibility=fields.String,
        created_at=fields.DateTime(dt_format="iso8601"),
        updated_at=fields.DateTime(dt_format="iso8601"),
        is_active=fields.Boolean,
    )

    @classmethod
    def all(cls):
        return cls.__fields
