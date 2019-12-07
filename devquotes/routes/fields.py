from flask import request
from flask_restful import fields


class PaginationUrl(fields.Raw):
    def format(self, value):
        if value is None:
            return None

        return '{}?page={}'.format(request.path, value)


user_fields = {
    'data': {
        'is_admin': fields.Boolean,
    }
}

quote_fields = {
    'data': {
        'id': fields.Integer,
        'author': fields.String,
        'quotation': fields.String,
        'source': fields.String,
        'likes': fields.Integer,
        'created_at': fields.DateTime(dt_format='iso8601'),
        'updated_at': fields.DateTime(dt_format='iso8601'),
    }
}

quotes_fields = {
    'curr_page': fields.Integer(attribute='page'),
    'next_page': PaginationUrl(attribute='next_num'),
    'prev_page': PaginationUrl(attribute='prev_num'),
    'per_page': fields.Integer(attribute='per_page'),
    'total': fields.Integer(attribute='total'),
    'data': fields.List(fields.Nested(quote_fields), attribute='items'),
}
