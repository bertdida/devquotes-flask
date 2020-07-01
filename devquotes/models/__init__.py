from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_searchable import make_searchable

db = SQLAlchemy()
make_searchable(db.metadata)

migrate = Migrate(compare_type=True)


def init_app(app):
    app.app_context().push()

    db.init_app(app)
    migrate.init_app(app, db)
