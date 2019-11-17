from sqlalchemy.dialects.postgresql import UUID

from ..db import DB

TeamMembers = DB.Table(
    "users_teams",
    DB.Column(
        "user_id", UUID(as_uuid=False), DB.ForeignKey("users.id"), nullable=False
    ),
    DB.Column(
        "team_id", UUID(as_uuid=False), DB.ForeignKey("teams.id"), nullable=False
    ),
    DB.PrimaryKeyConstraint("user_id", "team_id"),
)
