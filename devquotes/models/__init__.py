from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate(compare_type=True)


def init_app(app):
    app.app_context().push()

    db.init_app(app)
    migrate.init_app(app, db)
