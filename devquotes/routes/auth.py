from flask_restful import (
    abort,
    marshal_with,
    Resource,
    reqparse,
)
from flask import current_app
from firebase_admin import auth

from .fields import user_fields
from devquotes.models import db
from devquotes.models.user import User


class Token(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=str, required=True)

    @marshal_with(user_fields)
    def post(self):
        args = self.parser.parse_args()

        try:
            firebase_user = auth.verify_id_token(args['token'])
        except Exception:  # pylint: disable=broad-except
            abort(401)

        firebase_user_id = firebase_user['user_id']
        user = User.query.filter_by(firebase_user_id=firebase_user_id).scalar()
        if not user:
            user = User()
            user.firebase_user_id = firebase_user_id
            user.is_admin = firebase_user['email'] in current_app.config['ADMINS']

            db.session.add(user)
            db.session.commit()

        return user
