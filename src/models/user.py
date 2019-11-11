import uuid
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB


class User(DB.Model):

    __tablename__ = "users"

    id = DB.Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4().hex)
    first_name = DB.Column(DB.String, nullable=False)
    last_name = DB.Column(DB.String, nullable=False)
    username = DB.Column(DB.String, nullable=False)
    email = DB.Column(DB.String, nullable=False)
    password_hash = DB.Column(DB.String, nullable=False)
    visibility = DB.Column(DB.String, server_default="public")
    created_at = DB.Column(DB.DateTime, server_default="now")
    updated_at = DB.Column(DB.DateTime, server_default="now")
    is_active = DB.Column(DB.Boolean, server_default="true")

    def __repr__(self):
        return f"<User(first_name='{self.first_name}', last_name='{self.last_name}')>"
