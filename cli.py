"""This module registers custom flask commands."""

import json
import os
import re

from sqlalchemy.exc import DataError, IntegrityError

from devquotes.models import db
from devquotes.models.user import User
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus


def register(app):
    """Call this function passing the Flask app."""

    # pylint: disable=unused-variable

    @app.cli.command()
    def seed():
        """Seeds the database."""

        if not User.get_by(first=True, is_admin=True):
            print('Atleast one admin user should exists in database to continue seeding.')
            return

        json_path = './seeder'
        json_files = get_filenames(json_path)

        for json_file in json_files:
            with open(f'{json_path}/{json_file}') as in_file:
                json_data = json.load(in_file)
                data = json_data['data']
                model_name = json_data['model']

                if model_name == 'QuoteStatus':
                    _seed_quote_status(data)

                elif model_name == 'Quote':
                    admin = User.get_by(first=True, is_admin=True)
                    status = QuoteStatus\
                        .get_by(first=True, name=app.config['PUBLISHED_STATUS_NAME'])

                    _seed_quote(
                        data,
                        status_id=status.id,
                        contributor_id=admin.id,
                    )

    @app.cli.command()
    def deletespams():
        spam_status = QuoteStatus.get_by(first=True, name='spam')
        row_count = Quote.query.filter_by(status_id=spam_status.id).delete()
        db.session.commit()

        print(f'Deleted {row_count} spam quote/s.')


def get_filenames(path):
    """Returns the JSON filenames on the given `path` sorted
    by name naturally."""

    filenames = [
        filename for filename in os.listdir(path)
        if filename.endswith('.json')
    ]

    return natsort(filenames)


def natsort(seq, natsort_re=re.compile(r'([0-9]+)')):
    """Sorts an iterable naturally."""

    def convert(text):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(natsort_re, text)
        ]

    seq.sort(key=convert)
    return seq


def _seed_quote_status(data):
    """Seeds quote statuses."""

    for curr_data in data:
        try:
            QuoteStatus.create(**curr_data)
        except IntegrityError as error:
            print(error)


def _seed_quote(data, status_id, contributor_id):
    """Seeds quotes."""

    for curr_data in data:
        curr_data['status_id'] = status_id
        curr_data['contributor_id'] = contributor_id

        try:
            Quote.create(**curr_data)
        except (DataError, IntegrityError) as error:
            print(error)
