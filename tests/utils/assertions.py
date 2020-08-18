from os.path import join, dirname

import jsonref
from jsonschema import validate


def assert_post_data_in_response(data, response):
    json = response.json
    for key, value in data.items():
        assert json['data'][key] == value


def assert_valid_schema(response, schema_file):
    schema = _load_json_schema(schema_file)
    return validate(response.json, schema)


def assert_valid_status_code(response, status_code):
    assert response.status_code == status_code


def _load_json_schema(filename):
    relative_path = join('schemas', filename)
    absolute_path = join(dirname(__file__), relative_path)

    base_path = dirname(absolute_path)
    base_uri = f'file:///{base_path}/'

    with open(absolute_path) as schema_file:
        return jsonref.loads(schema_file.read(), base_uri=base_uri, jsonschema=True)
