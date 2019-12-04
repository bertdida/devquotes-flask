from flask import Flask


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    from devquotes import models, routes
    models.init_app(app)
    routes.init_app(app)

    return app
