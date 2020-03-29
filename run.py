import json
import operator
import os
from random import shuffle

from sqlalchemy.exc import DataError

from devquotes import create_app
from devquotes.models import db
from devquotes.models.user import User  # pylint: disable=unused-import
from devquotes.models.quote import Quote  # pylint: disable=unused-import
from devquotes.models.like import Like  # pylint: disable=unused-import

app = create_app(config_class=os.environ['CONFIG_CLASS'])


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


@app.before_first_request
def create_database_tables():
    db.create_all()


@app.cli.command()
def routes():
    rules = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        rules.append((rule.endpoint, methods, str(rule)))

    sort_by_rule = operator.itemgetter(2)
    for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
        route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
        print(route)


@app.cli.command()
def seed():
    with open('quotes.json') as json_file:
        quotes = json.load(json_file)
        shuffle(quotes)

        for data in quotes:
            try:
                Quote.create(**data)
            except DataError:
                pass


def _write_firebase_creds_to_file(filename, creds):
    creds_escaped = creds.encode().decode('unicode_escape')
    creds_json = json.loads(creds_escaped)

    with open(filename, 'w') as creds_file:
        json.dump(creds_json, creds_file)


if __name__ == '__main__':
    firebase_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    firebase_creds_filename = 'firebase.json'

    if not os.path.isfile(firebase_creds_filename) and firebase_creds is not None:
        _write_firebase_creds_to_file(firebase_creds_filename, firebase_creds)

    app.run()
