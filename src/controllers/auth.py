import bcrypt

from ..models import User


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return user


def identity(payload):
    user_id = payload["identity"]
    return User.query.filter_by(id=user_id).first()
