import uuid
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB


class Team(DB.Model):
    __tablename__ = "teams"

    id = DB.Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = DB.Column(DB.String, nullable=False)
    created_at = DB.Column(DB.DateTime, server_default="now")
    updated_at = DB.Column(DB.DateTime, server_default="now")
    is_active = DB.Column(DB.Boolean, server_default="true")
