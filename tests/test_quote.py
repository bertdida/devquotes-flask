"""This module contains quote related tests."""

import pytest

from .test_auth import login
from .utils.assertions import (
    assert_valid_schema,
    assert_valid_status_code,
    assert_valid_search_results,
)


class Actions:
    """Class for common actions."""

    def __init__(self, client):
        self.client = client

    def get_quotes(self):
        """Gets quotes."""

        return self.client.get('/v1/quotes')

    def filter_quotes(self, **filters):
        """Filters quotes."""

        params = '&'.join(f'{k}={v}' for k, v in filters.items())
        return self.client.get(f'/v1/quotes?{params}')

    def get_quote(self, quote_id):
        """Gets quote by id."""

        return self.client.get(f'/v1/quotes/{quote_id}')

    def get_random_quote(self):
        """Gets random quote."""

        return self.client.get('/v1/quotes/random')

    def get_unidentified_quote(self):
        """Gets quote that doesn't exists."""

        return self.client.get('/v1/quotes/random/99')

    def get_quote_contributor(self, quote_id):
        """Gets quote's contributer for the given id."""

        return self.client.get(f'/v1/quotes/{quote_id}/contributor')

    def search_quotes(self, query):
        """Searches quotes."""

        return self.client.get(f'/v1/quotes?query={query}')

    def create_quote(self):
        """Creates quote."""

        post_data = {
            'author': 'Austin Freeman',
            'quotation': 'Simplicity is the soul of efficiency.',
        }

        return self.client.post('/v1/quotes', data=post_data)

    def update_quote(self, quote_id, post_data):
        """Updates quote by id."""

        return self.client.patch(f'/v1/quotes/{quote_id}', data=post_data)

    def publish_quote(self, quote_id):
        """Updates the status of the quote to `published`."""

        post_data = {'status': 'published'}
        return self.update_quote(quote_id, post_data)

    def flag_quote_as_spam(self, quote_id):
        """Updates the status of the quote to `spam`."""

        post_data = {'status': 'spam'}
        return self.update_quote(quote_id, post_data)

    def delete_quote(self, quote_id):
        """Deletes quote by id"""

        return self.client.delete(f'/v1/quotes/{quote_id}')

    def delete_quotes(self, *quote_ids):
        """Deletes multiple quotes."""

        params = ','.join(str(i) for i in quote_ids)
        return self.client.delete(f'/v1/quotes/?ids={params}')


class TestViewer:
    """Class for testing unauthenticated user."""

    @pytest.fixture(autouse=True)
    def init(self, client):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        self.actions = Actions(client)

    def test_get_quotes(self):
        """Tests unauthenticated user getting quotes."""

        resp = self.actions.get_quotes()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_filter_quotes(self):
        """Tests unauthenticated user filtering quotes."""

    def test_get_quote(self, quote):
        """Tests unauthenticated user getting a quote."""

        resp = self.actions.get_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_random_quote(self):
        """Tests unauthenticated user getting a random quote."""

        resp = self.actions.get_random_quote()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_unidentified_quote(self):
        """Tests unauthenticated user getting a non-existing quote."""

        resp = self.actions.get_unidentified_quote()
        assert_valid_status_code(resp, 404)

    def test_get_quote_contributor(self, quote):
        """Tests unauthenticated user getting quote's contributor."""

        resp = self.actions.get_quote_contributor(quote.id)
        assert_valid_status_code(resp, 401)

    def test_search_quotes(self, quote):
        """Tests unauthenticated user searching quotes."""

        resp = self.actions.search_quotes(quote.quotation)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
        assert_valid_search_results(resp, quote.quotation)
        assert resp.json['total'] >= 1

    def test_create_quote(self):
        """Tests unauthenticated user creating a quote."""

        resp = self.actions.create_quote()
        assert_valid_status_code(resp, 401)

    def test_update_quote(self, quote):
        """Tests unauthenticated user updating a quote."""

        post_data = {'author': 'unknown'}
        resp = self.actions.update_quote(quote.id, post_data)
        assert_valid_status_code(resp, 401)

    def test_publish_quote(self, quote):
        """Tests unauthenticated user updating quote's status to `published`."""

        resp = self.actions.publish_quote(quote.id)
        assert_valid_status_code(resp, 401)

    def test_flag_quote_as_spam(self, quote):
        """Tests unauthenticated user updating quote's status to `spam`."""

        resp = self.actions.flag_quote_as_spam(quote.id)
        assert_valid_status_code(resp, 401)

    def test_delete_quote(self, quote):
        """Tests unauthenticated user deleting a quote."""

        resp = self.actions.delete_quote(quote.id)
        assert_valid_status_code(resp, 401)

    def test_delete_quotes(self, quotes):
        """Tests unauthenticated user deleting multiple quotes."""

        ids = [q.id for q in quotes]
        resp = self.actions.delete_quotes(*ids)
        assert_valid_status_code(resp, 401)


class TestContributor:
    """Class for testing authenticated user."""

    @pytest.fixture(autouse=True)
    def init(self, client, user):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        login(client, user)
        self.actions = Actions(client)

    def test_get_quotes(self):
        """Tests authenticated user getting quotes."""

        resp = self.actions.get_quotes()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_filter_quotes(self):
        """Tests authenticated user filtering quotes."""

    def test_get_quote(self, quote):
        """Tests authenticated user getting a quote."""

        resp = self.actions.get_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_random_quote(self):
        """Tests authenticated user getting a random quote."""

        resp = self.actions.get_random_quote()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_unidentified_quote(self):
        """Tests authenticated user getting a non-existing quote."""

        resp = self.actions.get_unidentified_quote()
        assert_valid_status_code(resp, 404)

    def test_get_quote_contributor(self, quote):
        """Tests authenticated user getting quote's contributor."""

        resp = self.actions.get_quote_contributor(quote.id)
        assert_valid_status_code(resp, 403)

    def test_search_quotes(self, quote):
        """Tests authenticated user searching quotes."""

        resp = self.actions.search_quotes(quote.quotation)
        assert_valid_status_code(resp, 200)
        assert_valid_search_results(resp, quote.quotation)
        assert resp.json['total'] >= 1

    def test_create_quote(self):
        """Tests authenticated user creating a quote."""

        resp = self.actions.create_quote()
        assert_valid_status_code(resp, 201)
        assert_valid_schema(resp, 'quote.json')

    def test_update_quote(self, quote):
        """Tests authenticated user updating a quote."""

        post_data = {'author': 'unknown'}
        resp = self.actions.update_quote(quote.id, post_data)
        assert_valid_status_code(resp, 403)

    def test_publish_quote(self, quote):
        """Tests authenticated user updating quote's status to `published`."""

        resp = self.actions.publish_quote(quote.id)
        assert_valid_status_code(resp, 403)

    def test_flag_quote_as_spam(self, quote):
        """Tests authenticated user updating quote's status to `spam`."""

        resp = self.actions.flag_quote_as_spam(quote.id)
        assert_valid_status_code(resp, 403)

    def test_delete_quote(self, quote):
        """Tests authenticated user deleting a quote."""

        resp = self.actions.delete_quote(quote.id)
        assert_valid_status_code(resp, 403)

    def test_delete_quotes(self, quotes):
        """Tests authenticated user deleting multiple quotes."""

        ids = [q.id for q in quotes]
        resp = self.actions.delete_quotes(*ids)
        assert_valid_status_code(resp, 403)


class TestAdmin:
    """Class for testing admin user."""

    @pytest.fixture(autouse=True)
    def init(self, client, user_admin):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        login(client, user_admin)
        self.actions = Actions(client)

    def test_get_quotes(self):
        """Tests admin user getting quotes."""

        resp = self.actions.get_quotes()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_filter_quotes(self):
        """Tests admin user filtering quotes."""

    def test_get_quote(self, quote):
        """Tests admin user getting a quote."""

        resp = self.actions.get_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_random_quote(self):
        """Tests admin user getting a random quote."""

        resp = self.actions.get_random_quote()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_unidentified_quote(self):
        """Tests admin user getting a non-existing quote."""

        resp = self.actions.get_unidentified_quote()
        assert_valid_status_code(resp, 404)

    def test_get_quote_contributor(self, quote):
        """Tests admin user getting quote's contributor."""

        resp = self.actions.get_quote_contributor(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')

    def test_search_quotes(self, quote):
        """Tests admin user searching quotes."""

        resp = self.actions.search_quotes(quote.quotation)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
        assert_valid_search_results(resp, quote.quotation)
        assert resp.json['total'] >= 1

    def test_create_quote(self):
        """Tests admin user creating a quote."""

        resp = self.actions.create_quote()
        assert_valid_status_code(resp, 201)
        assert_valid_schema(resp, 'quote.json')

    def test_update_quote(self, quote):
        """Tests admin user updating a quote."""

        post_data = {'author': 'unknown'}
        resp = self.actions.update_quote(quote.id, post_data)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_publish_quote(self, quote):
        """Tests admin user updating quote's status to `published`."""

        resp = self.actions.publish_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_flag_quote_as_spam(self, quote):
        """Tests admin user updating quote's status to `spam`."""

        resp = self.actions.flag_quote_as_spam(quote.id)
        assert_valid_status_code(resp, 200)

    def test_delete_quote(self, quote):
        """Tests admin user deleting a quote."""

        resp = self.actions.delete_quote(quote.id)
        assert_valid_status_code(resp, 204)

    def test_delete_quotes(self, quotes):
        """Tests admin user deleting multiple quotes."""

        ids = [q.id for q in quotes]
        resp = self.actions.delete_quotes(*ids)
        assert_valid_status_code(resp, 200)
