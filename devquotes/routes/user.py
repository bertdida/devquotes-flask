from flask_restful import (
    marshal_with,
    Resource,
)

from . import db_client
from .fields import user_fields


class User(Resource):

    @marshal_with(user_fields)
    def get(self, user_id):
        return db_client.get_user_or_404(user_id)
