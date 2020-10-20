"""This module contains `BaseMixin` class."""

from devquotes.models import db


class BaseMixin:
    """A mixin for common database operations."""

    __table_args__ = {'extend_existing': True}

    @classmethod
    def get(cls, model_id):
        """Returns model by `id`.

        Args:
            model_id (int): The `id` of the model to return.
        """

        return cls.query.get(int(model_id))

    @classmethod
    def get_or_404(cls, model_id):
        """Like `get` but aborts with 404 if model not found
        instead of returning `None`."""

        return cls.query.get_or_404(int(model_id))

    @classmethod
    def get_by(cls, first=False, **kwargs):
        """Applies the given filtering criterion to the model,
        using keyword expressions."""

        rows = cls.query.filter_by(**kwargs)
        if first:
            return rows.first()

        return rows.all()

    @classmethod
    def create(cls, **kwargs):
        """Creates a new record to the database."""

        instance = cls(**kwargs)
        return instance.save()

    def save(self, commit=True):
        """Saves the current transaction if `commit` is `True`."""

        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return self

    def update(self, commit=True, **kwargs):
        """Updates a record to the database."""

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        if commit:
            return self.save()

        return self

    def delete(self, commit=True):
        """Deletes a record from the database."""

        db.session.delete(self)
        if not commit:
            return None

        return db.session.commit()
