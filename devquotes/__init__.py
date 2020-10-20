"""This module contains the app factory function."""

from flask import Flask
from devquotes import models, routes


def create_app(config_class):
    """The app factory function.

    Args:
        config_class (string): The name of the configuration class.

    Returns:
        Flask: The Flask app instance.
    """

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    models.init_app(app)
    routes.init_app(app)

    return app
