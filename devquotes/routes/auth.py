"""This module contains authorization API."""

from firebase_admin import auth
from firebase_admin.auth import (
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)
from flask import (
    current_app,
    jsonify,
    make_response
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
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
    """Resource for getting access and refresh tokens."""

    @classmethod
    def post(cls):
        """Sets tokens in cookies."""

        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str, required=True)
        args = parser.parse_args()

        try:
            firebase_user = auth.verify_id_token(args['token'])
        except (ValueError, InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError) as error:
            abort(401, message=str(error))

        user = db_client.get_user(firebase_user_id=firebase_user['user_id'])
        if not user:
            user = db_client.create_user({
                'firebase_user_id': firebase_user['user_id'],
                'is_admin': firebase_user['email'] in current_app.config['ADMINS'],
                'name': firebase_user['name'],
                'picture_url': firebase_user['picture'],
            })

        identity = {
            'firebase_user_id': user.firebase_user_id,
            'is_admin': user.is_admin,
            'id': user.id,
        }
        access_token = create_access_token(identity)
        refresh_token = create_refresh_token(identity)

        response = jsonify(marshal(user, user_fields))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response


class TokenRefresh(Resource):
    """Resource for refreshing access token."""

    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        """Sets a refreshed token in cookies."""

        identity = get_jwt_identity()
        access_token = create_access_token(identity)

        response = jsonify({})
        set_access_cookies(response, access_token)
        return response


class TokenRevoke(Resource):
    """Resource for unsetting tokens."""

    @classmethod
    @jwt_required
    def post(cls):
        """Removes token in cookies."""

        response = jsonify({})
        unset_jwt_cookies(response)
        return make_response(response, 204)
