from flask_restful import fields

COMMON_FIELDS = dict(
    id=fields.String,
    created_at=fields.DateTime(dt_format="iso8601"),
    updated_at=fields.DateTime(dt_format="iso8601"),
    is_active=fields.Boolean,
)
