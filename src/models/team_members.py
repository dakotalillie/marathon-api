from sqlalchemy.dialects.postgresql import UUID

from ..db import DB

TEAM_MEMBERS = DB.Table(
    "users_teams",
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
    DB.PrimaryKeyConstraint("user_id", "team_id"),
)
