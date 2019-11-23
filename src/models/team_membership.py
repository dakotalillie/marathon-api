from datetime import datetime
import uuid

from flask_restful import fields
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB
from ..utils.marshaller import CommonMarshaller


class TeamMembership(DB.Model):
    __tablename__ = "team_memberships"
    __table_args__ = ((DB.UniqueConstraint("user_id", "team_id")),)

    id = DB.Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    updated_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean, default=True)
    user_id = DB.Column(
        UUID(as_uuid=False),
        DB.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_id = DB.Column(
        UUID(as_uuid=False),
        DB.ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )

    marshaller = CommonMarshaller({"team_id": fields.String, "user_id": fields.String})
