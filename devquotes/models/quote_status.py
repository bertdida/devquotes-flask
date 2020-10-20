"""This module defines the structure of quote_status table."""

from . import db
from .mixins import BaseMixin


class QuoteStatus(db.Model, BaseMixin):
    """A model to store quote status related data."""

    __tablename__ = 'quote_status'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(25), nullable=False, unique=True)
    display_name = db.Column(db.String(50), nullable=False)

    quotes = db.relationship('Quote', back_populates='status')
