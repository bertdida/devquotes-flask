"""Runs the application."""

import os

import cli
from devquotes import create_app
from devquotes.models import db
from devquotes.models.like import Like
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus
from devquotes.models.user import User

app = create_app(config_class=os.environ['CONFIG_CLASS'])
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    """Registers relevant shell contexts."""

    return {
        'db': db,
        'User': User,
        'Quote': Quote,
        'QuoteStatus': QuoteStatus,
        'Like': Like,
    }


@app.before_first_request
def create_database_tables():
    """Creates database tables."""

    db.configure_mappers()
    db.create_all()


def main():
    """The starting point of the app."""

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


if __name__ == '__main__':
    main()
