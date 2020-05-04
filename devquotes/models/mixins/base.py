# pylint: disable=redefined-builtin
from devquotes.models import db


class BaseMixin:
    __table_args__ = {'extend_existing': True}

    @classmethod
    def get(cls, id):
        return cls.query.get(int(id))

    @classmethod
    def get_or_404(cls, id):
        return cls.query.get_or_404(int(id))

    @classmethod
    def get_by(cls, first=False, **kwargs):
        rows = cls.query.filter_by(**kwargs)
        if first:
            return rows.first()
        return rows.all()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

        if commit:
            return self.save()
        return self

    def delete(self, commit=True):
        db.session.delete(self)

        if commit:
            return db.session.commit()
