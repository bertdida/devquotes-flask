import os

from devquotes import create_app
from devquotes.models import db
from devquotes.models.user import User  # pylint: disable=unused-import
from devquotes.models.quote import Quote  # pylint: disable=unused-import
from devquotes.models.like import Like  # pylint: disable=unused-import

app = create_app(config_class=os.environ['CONFIG_CLASS'])


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
    app.run()
