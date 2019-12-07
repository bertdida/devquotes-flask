from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api()


def init_app(app):
    from flask_jwt_extended import JWTManager
    jwt = JWTManager()
    jwt.init_app(app)

    import firebase_admin
    firebase_admin.initialize_app()

    from .auth import Token
    from .quote import QuoteList

    api.init_app(bp)
    api.add_resource(Token, '/auth/token')
    api.add_resource(QuoteList, '/quotes')

    app.register_blueprint(bp, url_prefix='/v1')
