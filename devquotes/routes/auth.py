from firebase_admin import auth
from flask import (
    current_app,
    jsonify,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
)
from flask_restful import (
    abort,
    marshal,
    Resource,
    reqparse,
)

from . import db_client
from .fields import user_fields


class Token(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=str, required=True)

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

        identity = {
            'firebase_user_id': user.firebase_user_id,
            'is_admin': user.is_admin,
        }
        access_token = create_access_token(identity)
        refresh_token = create_refresh_token(identity)

        response = jsonify(marshal(user, user_fields))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response
