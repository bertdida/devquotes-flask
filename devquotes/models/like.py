
from . import db
from .mixins import BaseMixin


class Like(BaseMixin, db.Model):
    __tablename__ = 'like'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'quote_id'),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
