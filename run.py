import json
import os

import click
from sqlalchemy.exc import DataError, IntegrityError

from devquotes import create_app
from devquotes.models import db
from devquotes.models.like import Like  # pylint: disable=unused-import
from devquotes.models.quote import Quote  # pylint: disable=unused-import
from devquotes.models.quote_type import QuoteType  # pylint: disable=unused-import
from devquotes.models.user import User  # pylint: disable=unused-import

app = create_app(config_class=os.environ['CONFIG_CLASS'])


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Quote': Quote,
        'QuoteType': QuoteType,
        'Like': Like,
    }


@app.before_first_request
def create_database_tables():
    db.configure_mappers()
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
        except (DataError, IntegrityError):
            pass


if __name__ == '__main__':
    in_dev = app.config.get('ENV') == 'development'
    server_name = app.config.get('SERVER_NAME')

    ssl_context = None
    if in_dev and server_name:
        host_name = server_name.split(':')[0]
        cert_file = './ssl/{}.pem'.format(host_name)
        pkey_file = './ssl/{}-key.pem'.format(host_name)

        if os.path.isfile(cert_file) and os.path.isfile(pkey_file):
            ssl_context = (cert_file, pkey_file)

    app.run(ssl_context=ssl_context)
