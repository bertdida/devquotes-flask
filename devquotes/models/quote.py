"""This module defines the structure of quote table."""

from datetime import datetime

from slugify import slugify
from sqlalchemy import event
from sqlalchemy_utils.types import TSVectorType

from . import db
from .mixins import BaseMixin

utcnow = datetime.utcnow


class Quote(db.Model, BaseMixin):
    """A model to store quote related data."""

    __tablename__ = 'quote'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    quotation = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String, nullable=True)
    total_likes = db.Column(db.Integer, nullable=False, default=0)
    slug = db.Column(db.String(200), nullable=True)

    contributor_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False
    )
    contributor = db.relationship('User', back_populates='contributed_quotes')

    status_id = db.Column(
        db.Integer, db.ForeignKey('quote_status.id'), nullable=False
    )
    status = db.relationship('QuoteStatus', back_populates='quotes')

    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    search_vector = db.deferred(db.Column(
        TSVectorType(
            'quotation', 'author',
            weights={'quotation': 'A', 'author': 'B'}
        ),
        nullable=False
    ))

    @staticmethod
    def slugify(target, value, oldvalue, _):
        """Sets `slug` property for the given `target` object."""

        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


event.listen(Quote.quotation, 'set', Quote.slugify, retval=False)
