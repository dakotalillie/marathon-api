from flask_jwt_extended import get_jwt_identity
from flask_restful import fields
from sqlalchemy.dialects.postgresql import UUID

from .common_mixin import CommonMixin
from ..db import DB
from ..utils.marshaller import CommonMarshaller


class Team(CommonMixin, DB.Model):
    __tablename__ = "teams"

    name = DB.Column(DB.String, nullable=False)
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

    marshaller = CommonMarshaller(
        {
            "name": fields.String,
            "created_by": fields.String,
            "updated_by": fields.String,
        }
    )
