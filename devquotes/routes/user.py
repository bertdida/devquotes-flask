from flask_jwt_extended import jwt_required
from flask_restful import marshal_with, Resource

from . import db_client
from .fields import user_fields
from .utils import admin_only


class User(Resource):

    @marshal_with(user_fields)
    @jwt_required
    @admin_only
    def get(self, user_id):
        return db_client.get_user_or_404(user_id)
