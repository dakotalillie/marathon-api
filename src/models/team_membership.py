from flask_jwt_extended import get_jwt_identity
from flask_restful import fields
from sqlalchemy.dialects.postgresql import UUID

from .common_mixin import CommonMixin
from ..db import DB
from ..utils.marshaller import CommonMarshaller


class TeamMembership(CommonMixin, DB.Model):
    __tablename__ = "team_memberships"
    __table_args__ = ((DB.UniqueConstraint("user_id", "team_id")),)

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
    created_by = DB.Column(
        UUID(as_uuid=False),
        DB.ForeignKey("users.id", ondelete="SET NULL"),
        default=get_jwt_identity,
        nullable=True,
    )
    updated_by = DB.Column(
        UUID(as_uuid=False),
        DB.ForeignKey("users.id", ondelete="SET NULL"),
        default=get_jwt_identity,
        nullable=True,
    )
    user = DB.relationship(
        "User",
        backref=DB.backref("team_memberships"),
        foreign_keys=[user_id],
        viewonly=True,
    )
    team = DB.relationship(
        "Team",
        backref=DB.backref("team_memberships"),
        foreign_keys=[team_id],
        viewonly=True,
    )

    marshaller = CommonMarshaller(
        {
            "team_id": fields.String,
            "user_id": fields.String,
            "created_by": fields.String,
            "updated_by": fields.String,
        }
    )
