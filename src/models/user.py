import uuid
import bcrypt
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB
from .users_teams import TeamMembers


class User(DB.Model):
    __tablename__ = "users"

    id = DB.Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name = DB.Column(DB.String, nullable=False)
    last_name = DB.Column(DB.String, nullable=False)
    username = DB.Column(DB.String, nullable=False, unique=True)
    email = DB.Column(DB.String, nullable=False, unique=True)
    password_hash = DB.Column(DB.String, nullable=False)
    visibility = DB.Column(DB.String, server_default="public")
    created_at = DB.Column(DB.DateTime, server_default="now")
    updated_at = DB.Column(DB.DateTime, server_default="now")
    is_active = DB.Column(DB.Boolean, server_default="true")
    teams = DB.relationship(
        "Team",
        secondary=TeamMembers,
        lazy="subquery",
        backref=DB.backref("users", lazy=True),
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
