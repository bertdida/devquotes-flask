from firebase_admin import auth
from flask import current_app
from flask_restful import (
    abort,
    marshal_with,
    Resource,
    reqparse,
)

from . import db_client
from .fields import user_fields


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

        user = db_client.get_user(firebase_user_id=firebase_user['user_id'])
        if not user:
            user = db_client.create_user({
                'firebase_user_id': firebase_user['user_id'],
                'is_admin': firebase_user['email'] in current_app.config['ADMINS']
            })

        return user
