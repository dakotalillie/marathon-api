import bcrypt

from ..models import User


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user.has_password(password):
        return user


def identity(payload):
    user_id = payload["identity"]
    return User.query.filter_by(id=user_id).first()
