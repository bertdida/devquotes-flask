"""This module contains registers the URL for the API."""

from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api()

# pylint: disable=too-many-locals


def init_app(app):
    """Register this extension with the Flask app."""

    # pylint: disable=import-outside-toplevel

    from flask_cors import CORS
    from flask_jwt_extended import JWTManager

    allowed_origins = app.config['ALLOWED_ORIGINS']
    CORS(app, supports_credentials=True, origins=allowed_origins)

    jwt = JWTManager()
    jwt.init_app(app)

    import json
    import firebase_admin

    creds = app.config['FIREBASE_CREDENTIAL']

    try:
        credential = firebase_admin.credentials.Certificate(cert=creds)
    except FileNotFoundError:
        creds_escaped = creds.encode().decode('unicode_escape')
        creds_dict = json.loads(creds_escaped, strict=False)
        credential = firebase_admin.credentials.Certificate(cert=creds_dict)

    firebase_admin.initialize_app(credential=credential)

    from .auth import Token, TokenRevoke, TokenRefresh
    from .quote import Quotes, Quote, Random as RandomQuote, Contributor
    from .like import Likes, Like
    from .user import User, CurrentUser
    from .quote_status import QuoteStatus

    api.init_app(bp)
    api.add_resource(Token, '/auth/token')
    api.add_resource(TokenRefresh, '/auth/refresh')
    api.add_resource(TokenRevoke, '/auth/revoke')
    api.add_resource(Quotes, '/quotes')
    api.add_resource(Quote, '/quotes/<int:quote_id>')
    api.add_resource(RandomQuote, '/quotes/random')
    api.add_resource(Likes, '/likes')
    api.add_resource(Like, '/likes/<int:quote_id>')
    api.add_resource(User, '/users/<int:user_id>')
    api.add_resource(CurrentUser, '/users/me')
    api.add_resource(Contributor, '/quotes/<int:quote_id>/contributor')
    api.add_resource(QuoteStatus, '/quote-statuses')

    app.register_blueprint(bp, url_prefix='/v1')
