from datetime import datetime
import uuid

from flask_restful import fields
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB
from ..utils.marshaller import CommonMarshaller


class Team(DB.Model):
    __tablename__ = "teams"

    id = DB.Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    updated_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean, default=True)
    name = DB.Column(DB.String, nullable=False)
    team_memberships = DB.relationship(
        "TeamMembership",
        lazy="subquery",
        backref=DB.backref("team", lazy=True),
        viewonly=True,
    )

    marshaller = CommonMarshaller({"name": fields.String})
