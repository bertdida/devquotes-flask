from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api()


def init_app(app):
    from flask_cors import CORS
    from flask_jwt_extended import JWTManager

    CORS(app)

    jwt = JWTManager()
    jwt.init_app(app)

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'

    import json
    import firebase_admin

    creds = app.config['FIREBASE_CREDENTIAL']
    creds_escaped = creds.encode().decode('unicode_escape')
    creds_dict = json.loads(creds_escaped)

    credential = firebase_admin.credentials.Certificate(cert=creds_dict)
    firebase_admin.initialize_app(credential=credential)

    from .auth import Token, TokenRevoke, TokenRefresh
    from .quote import Quotes, Quote
    from .likes import Likes, Like

    api.init_app(bp)
    api.add_resource(Token, '/auth/token')
    api.add_resource(TokenRefresh, '/auth/refresh')
    api.add_resource(TokenRevoke, '/auth/revoke')
    api.add_resource(Quotes, '/quotes')
    api.add_resource(Quote, '/quotes/<int:quote_id>')
    api.add_resource(Likes, '/likes')
    api.add_resource(Like, '/likes/<int:quote_id>')

    app.register_blueprint(bp, url_prefix='/v1')
