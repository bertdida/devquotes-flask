from flask_jwt_extended import jwt_required
from flask_restful import abort, marshal_with, Resource

from . import db_client
from .fields import user_fields
from .utils import admin_only


class User(Resource):

    @marshal_with(user_fields)
    @jwt_required
    @admin_only
    def get(self, user_id):
        user = db_client.get_user_by_id(user_id)
        if user is None:
            abort(404)

        return user
