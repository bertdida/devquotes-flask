from datetime import datetime

from sqlalchemy_utils.types import TSVectorType

from . import db
from .mixins import BaseMixin

utcnow = datetime.utcnow


class Quote(db.Model, BaseMixin):
    __tablename__ = 'quote'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    quotation = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String, nullable=True)
    total_likes = db.Column(db.Integer, nullable=False, default=0)

    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # noqa
    contributor = db.relationship('User', back_populates='contributed_quotes')

    status_id = db.Column(db.Integer, db.ForeignKey('quote_status.id'), nullable=False)  # noqa
    status = db.relationship('QuoteStatus', back_populates='quotes')

    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)  # noqa

    search_vector = db.deferred(db.Column(
        TSVectorType(
            'quotation', 'author',
            weights={'quotation': 'A', 'author': 'B'}
        ),
        nullable=False
    ))
