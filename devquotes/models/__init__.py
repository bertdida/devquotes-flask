from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, BaseQuery

from sqlalchemy_searchable import SearchQueryMixin, make_searchable


class SearchQuery(BaseQuery, SearchQueryMixin):
    """Special class for enabling search on a table."""


db = SQLAlchemy(query_class=SearchQuery)
make_searchable(db.metadata)

migrate = Migrate(compare_type=True)


def init_app(app):
    app.app_context().push()

    db.init_app(app)
    migrate.init_app(app, db)
