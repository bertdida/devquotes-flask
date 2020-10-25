"""This module registers custom flask commands."""

import json
import os

from sqlalchemy.exc import DataError, IntegrityError

from devquotes.models.user import User
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus


def register(app):
    """Call this function passing the Flask app."""

    @app.cli.command()
    def seed():  # pylint: disable=unused-variable
        """Seeds the database."""

        if not User.get_by(first=True, is_admin=True):
            print('Atleast one admin user should exists in database to continue seeding.')
            return

        seeder_path = './seeder'
        json_files = [
            filename for filename in os.listdir(seeder_path)
            if filename.endswith('.json')
        ]

        for json_file in json_files:
            with open(f'{seeder_path}/{json_file}') as in_file:
                json_data = json.load(in_file)
                data = json_data['data']
                model_name = json_data['model']

                if model_name == 'QuoteStatus':
                    _seed_quote_status(data)

                elif model_name == 'Quote':
                    _seed_quote(data)


def _seed_quote_status(data):
    """Seeds quote statuses."""

    for curr_data in data:
        try:
            QuoteStatus.create(**curr_data)
        except IntegrityError as error:
            print(error)


def _seed_quote(data):
    """Seeds quotes."""

    admin = User.get_by(first=True, is_admin=True)
    published_status = QuoteStatus.get_by(first=True, name='published')

    status_id = published_status.id
    contributor_id = admin.id

    for curr_data in data:
        curr_data['status_id'] = status_id
        curr_data['contributor_id'] = contributor_id

        try:
            Quote.create(**curr_data)
        except (DataError, IntegrityError) as error:
            print(error)
