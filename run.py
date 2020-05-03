import json
import os

import click
from sqlalchemy.exc import DataError

from devquotes import create_app
from devquotes.models import db
from devquotes.models.user import User  # pylint: disable=unused-import
from devquotes.models.quote import Quote  # pylint: disable=unused-import
from devquotes.models.like import Like  # pylint: disable=unused-import

app = create_app(config_class=os.environ['CONFIG_CLASS'])


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Quote': Quote,
        'Like': Like,
    }


@app.before_first_request
def create_database_tables():
    db.create_all()


@app.cli.command()
@click.option(
    '--filename',
    required=True,
    type=click.File('rb'),
    help='The JSON file to parse.'
)
def seed(filename):
    """Populate `quote` table in database."""

    try:
        quotes = json.load(filename)
    except json.decoder.JSONDecodeError as e:
        raise click.BadParameter(e)

    for data in quotes:
        try:
            Quote.create(**data)
        except DataError:
            pass


if __name__ == '__main__':
    app.run()
