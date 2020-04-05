import json
import os
from random import shuffle

from sqlalchemy.exc import DataError

from devquotes import create_app
from devquotes.models import db
from devquotes.models.user import User  # pylint: disable=unused-import
from devquotes.models.quote import Quote  # pylint: disable=unused-import
from devquotes.models.like import Like  # pylint: disable=unused-import

app = create_app(config_class=os.environ['CONFIG_CLASS'])


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


@app.before_first_request
def create_database_tables():
    db.create_all()


@app.cli.command()
def seed():
    with open('quotes.json') as json_file:
        quotes = json.load(json_file)
        shuffle(quotes)

        for data in quotes:
            try:
                Quote.create(**data)
            except DataError:
                pass


if __name__ == '__main__':
    app.run()
