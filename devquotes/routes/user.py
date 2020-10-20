"""This module contains the users API."""

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import abort, marshal_with, Resource

from . import db_client
from .fields import user_fields
from .utils import admin_only


class User(Resource):
    """Resource for user."""

    @classmethod
    @marshal_with(user_fields)
    @jwt_required
    @admin_only
    def get(cls, user_id):
        """Returns user by id."""

        user = db_client.get_user_by_id(user_id)
        if user is None:
            abort(404)

        return user


class CurrentUser(Resource):
    """Resource for current user."""

    @classmethod
    @marshal_with(user_fields)
    @jwt_required
    def get(cls):
        """Returns the current user."""

        current_user = get_jwt_identity()
        return db_client.get_user_by_id(current_user['id'])
