from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from flask_restful import (
    marshal_with,
    reqparse,
    Resource,
)

from . import db_client
from .fields import quotes_fields


class UserLikes(Resource):

    @marshal_with(quotes_fields)
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        current_user = get_jwt_identity()
        return db_client.get_user_liked_quotes(current_user['id'], page, per_page)
