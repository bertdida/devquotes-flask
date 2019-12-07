from flask_restful import fields


user_fields = {
    'is_admin': fields.Boolean,
}

quote_fields = {
    'id': fields.Integer,
    'author': fields.String,
    'quotation': fields.String,
    'source': fields.String,
    'likes': fields.Integer,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
}
