from datetime import datetime
import uuid

import bcrypt
from flask_restful import fields
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB
from ..utils.marshaller import CommonMarshaller


class User(DB.Model):
    __tablename__ = "users"

    id = DB.Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    updated_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean, default=True)
    first_name = DB.Column(DB.String, nullable=False)
    last_name = DB.Column(DB.String, nullable=False)
    username = DB.Column(DB.String, nullable=False, unique=True)
    email = DB.Column(DB.String, nullable=False, unique=True)
    password_hash = DB.Column(DB.String, nullable=False)
    visibility = DB.Column(DB.String, server_default="public")
    team_memberships = DB.relationship(
        "TeamMembership",
        lazy="subquery",
        backref=DB.backref("user", lazy=True),
        viewonly=True,
    )
    teams = DB.relationship(
        "Team",
        secondary="team_memberships",
        lazy="subquery",
        backref=DB.backref("members", lazy=True),
    )
    marshaller = CommonMarshaller(
        {
            "first_name": fields.String,
            "last_name": fields.String,
            "username": fields.String,
            "email": fields.String,
            "visibility": fields.String,
        }
    )

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def has_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def __repr__(self):
        return f"<User(first_name='{self.first_name}', last_name='{self.last_name}')>"
