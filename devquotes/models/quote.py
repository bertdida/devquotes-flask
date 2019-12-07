from datetime import datetime

from . import db
from .mixins import BaseMixin

utcnow = datetime.utcnow


class Quote(BaseMixin, db.Model):
    __tablename__ = 'quote'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    quotation = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String, nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
