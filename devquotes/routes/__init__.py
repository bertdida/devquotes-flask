from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api()


def init_app(app):
    from flask_jwt_extended import JWTManager
    jwt = JWTManager()
    jwt.init_app(app)

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'

    import firebase_admin
    firebase_admin.initialize_app()

    from .auth import Token, TokenRevoke
    from .quote import QuoteList, Quote

    api.init_app(bp)
    api.add_resource(Token, '/auth/token')
    api.add_resource(TokenRevoke, '/auth/revoke')
    api.add_resource(QuoteList, '/quotes')
    api.add_resource(Quote, '/quotes/<int:id>')

    app.register_blueprint(bp, url_prefix='/v1')
