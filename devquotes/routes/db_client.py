from devquotes.models.user import User
from devquotes.models.quote import Quote


def get_user(firebase_user_id):
    return User.get_by(first=True, firebase_user_id=firebase_user_id)


def create_user(data):
    return User.create(**data)


def create_quote(data):
    return Quote.create(**data)
