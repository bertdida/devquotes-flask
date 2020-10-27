"""This module defines the structure of user table."""

from sqlalchemy.sql.expression import func

from . import db
from .like import Like
from .quote import Quote
from .quote_status import QuoteStatus
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

    @property
    def total_likes(self):
        """Returns the total liked quotes of the user."""

        return (
            db.session
            .query(func.count(Like.user_id))
            .filter_by(user_id=self.id)
            .scalar()
        )

    @property
    def total_submitted(self):
        """Returns the total published quotes submitted by the user."""

        return (
            db.session
            .query(func.count(Quote.id))
            .join(QuoteStatus)
            .filter(QuoteStatus.name == 'published')
            .filter(Quote.contributor_id == self.id)
            .scalar()
        )
