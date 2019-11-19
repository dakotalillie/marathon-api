from datetime import datetime
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from ..db import DB


class TeamMembership(DB.Model):
    __tablename__ = "team_memberships"
    __table_args__ = ((DB.UniqueConstraint("user_id", "team_id")),)

    id = DB.Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
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
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    updated_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean, default=True)
