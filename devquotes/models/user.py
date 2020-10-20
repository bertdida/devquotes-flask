"""This module defines the structure of user table."""

from . import db
from .mixins import BaseMixin


class User(BaseMixin, db.Model):
    """A model to store user related data."""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    firebase_user_id = db.Column(db.String, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String, nullable=False)
    picture_url = db.Column(db.String, nullable=True)

    contributed_quotes = db.relationship('Quote', back_populates='contributor')
