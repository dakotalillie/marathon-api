from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from ..db import DB

TEAM_MEMBERS = DB.Table(
    "team_members",
    DB.Column(
        "user_id",
        UUID(as_uuid=False),
        DB.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    DB.Column(
        "team_id",
        UUID(as_uuid=False),
        DB.ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    ),
    DB.Column("created_at", DB.DateTime, default=datetime.utcnow),
    DB.Column("updated_at", DB.DateTime, default=datetime.utcnow),
    DB.Column("is_active", DB.Boolean, default=True),
    DB.PrimaryKeyConstraint("user_id", "team_id"),
)
