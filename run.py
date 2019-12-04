import os

from devquotes import create_app

from devquotes.models.user import User

app = create_app(config_class=os.environ['CONFIG_CLASS'])


@app.shell_context_processor
def make_shell_context():
    return {'User': User}


if __name__ == '__main__':
    app.run()
