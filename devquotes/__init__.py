from elasticsearch import (
    Elasticsearch,
    RequestsHttpConnection
)
from flask import Flask
from requests_aws4auth import AWS4Auth


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    app.es = None

    if app.config['ELASTICSEARCH_URL']:
        params = {'hosts': app.config['ELASTICSEARCH_URL']}
        if app.config['ENV'] == 'production':
            awsauth = AWS4Auth(
                app.config['AWS_ACCESS_KEY'],
                app.config['AWS_SECRET_KEY'],
                app.config['AWS_REGION'],
                'es'  # AWS service
            )

            params.update({
                'http_auth': awsauth,
                'use_ssl': True,
                'verify_certs': True,
                'connection_class': RequestsHttpConnection
            })

        app.es = Elasticsearch(**params)

    from devquotes import models, routes
    models.init_app(app)
    routes.init_app(app)

    return app
