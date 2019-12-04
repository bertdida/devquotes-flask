from . import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    firebase_user_id = db.Column(db.Integer, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
