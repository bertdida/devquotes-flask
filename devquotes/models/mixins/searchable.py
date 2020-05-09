# pylint: disable=protected-access
from flask import current_app
from sqlalchemy import case

from devquotes.models import db


class SearchableMixin:

    @staticmethod
    def _add_to_index(index, obj):
        if not current_app.es:
            return

        payload = {}
        for field in obj.__searchable__:
            payload[field] = getattr(obj, field)

        current_app.es.index(index=index, id=obj.id, body=payload)

    @staticmethod
    def _remove_from_index(index, obj):
        if not current_app.es:
            return

        current_app.es.delete(index=index, id=obj.id)

    @staticmethod
    def _query_index(index, query):
        if not current_app.es:
            return [], 0

        body = {
            'query': {
                'multi_match':
                    {
                        'query': query,
                        'fields': ['*']
                    }
            },
        }

        search = current_app.es.search(index=index, body=body)
        return [int(hit['_id']) for hit in search['hits']['hits']]

    @classmethod
    def search(cls, query):
        ids = cls._query_index(cls.__tablename__, query)
        if not ids:
            return cls.query.filter_by(id=0), 0

        whens = [(curr_id, index) for index, curr_id in enumerate(ids)]
        return cls.query.filter(cls.id.in_(ids)).order_by(case(whens, cls.id))

    @classmethod
    def search_ids(cls, query):
        return cls._query_index(cls.__tablename__, query)

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                cls._add_to_index(obj.__tablename__, obj)

        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                cls._add_to_index(obj.__tablename__, obj)

        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                cls._remove_from_index(obj.__tablename__, obj)

        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            cls._add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
