from datetime import datetime

from sqlalchemy_utils.types import TSVectorType

from . import db
from .mixins import BaseMixin

utcnow = datetime.utcnow


class Quote(db.Model, BaseMixin):
    """ Model for storing quotes """

    __tablename__ = 'quote'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    quotation = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String, nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    search_vector = db.Column(
        TSVectorType(
            'quotation', 'author',
            weights={'quotation': 'A', 'author': 'B'}
        )
    )
