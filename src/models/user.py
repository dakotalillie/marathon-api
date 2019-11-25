import bcrypt
from flask_restful import fields
from sqlalchemy import Enum

from .common_mixin import CommonMixin
from ..db import DB
from ..utils.marshaller import CommonMarshaller


class User(CommonMixin, DB.Model):
    __tablename__ = "users"

    first_name = DB.Column(DB.String, nullable=False)
    last_name = DB.Column(DB.String, nullable=False)
    username = DB.Column(DB.String, nullable=False, unique=True)
    email = DB.Column(DB.String, nullable=False, unique=True)
    password_hash = DB.Column(DB.String, nullable=False)
    visibility = DB.Column(
        Enum("public", "private", name="visibility_enum"),
        nullable=False,
        server_default="public",
    )
    teams = DB.relationship(
        "Team",
        secondary="team_memberships",
        lazy="subquery",
        backref=DB.backref("members", lazy=True),
        primaryjoin="User.id == TeamMembership.user_id",
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
