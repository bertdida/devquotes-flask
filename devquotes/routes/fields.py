"""This module contains the format of the data to be returned
in the API response."""

from flask import request
from flask_restful import fields


class PaginationUrl(fields.Raw):
    """Pagination URL format."""

    def format(self, value):
        if value is None:
            return None

        return '{}?page={}'.format(request.path, value)


class Status(fields.Raw):
    """Quote status field."""

    def format(self, value):
        return value.name


user_fields = {
    'data': {
        'id': fields.Integer,
        'name': fields.String,
        'picture_url': fields.String,
        'is_admin': fields.Boolean,
        'total_likes': fields.Integer,
        'total_submitted': fields.Integer,
    }
}

quote_fields = {
    'data': {
        'id': fields.Integer,
        'author': fields.String,
        'quotation': fields.String,
        'source': fields.String,
        'total_likes': fields.Integer,
        'is_liked': fields.Boolean(default=False),
        'status': Status,
        'slug': fields.String,
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

quote_status_fields = {
    'data': {
        'id': fields.Integer,
        'name': fields.String,
        'display_name': fields.String,
    }
}

quotes_statuses_fields = {
    'data': fields.List(fields.Nested(quote_status_fields), attribute='items'),
}
