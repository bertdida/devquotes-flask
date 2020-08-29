# pylint: disable=attribute-defined-outside-init
import pytest

from .test_auth import login
from .utils.assertions import (
    assert_valid_schema,
    assert_valid_status_code,
    assert_valid_search_results,
)


class Actions:

    def __init__(self, client):
        self.client = client

    def get_quotes(self):
        return self.client.get('/v1/quotes')

    def filter_quotes(self, **filters):
        params = '&'.join(f'{k}={v}' for k, v in filters.items())
        return self.client.get(f'/v1/quotes?{params}')

    def get_quote(self, quote_id):
        return self.client.get(f'/v1/quotes/{quote_id}')

    def get_random_quote(self):
        return self.client.get('/v1/quotes/random')

    def get_unidentified_quote(self):
        return self.client.get('/v1/quotes/random/99')

    def get_quote_contributor(self, quote_id):
        return self.client.get(f'/v1/quotes/{quote_id}/contributor')

    def search_quotes(self, query):
        return self.client.get(f'/v1/quotes?query={query}')

    def create_quote(self):
        post_data = {
            'author': 'Austin Freeman',
            'quotation': 'Simplicity is the soul of efficiency.',
        }

        return self.client.post('/v1/quotes', data=post_data)

    def update_quote(self, quote_id):
        post_data = {
            'author': 'Unknown',
        }

        return self.client.patch(f'/v1/quotes/{quote_id}', data=post_data)

    def delete_quote(self, quote_id):
        return self.client.delete(f'/v1/quotes/{quote_id}')


class TestViewer:

    @pytest.fixture(autouse=True)
    def init(self, client):
        self.actions = Actions(client)

    def test_get_quotes(self):
        resp = self.actions.get_quotes()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_filter_quotes(self):
        pass

    def test_get_quote(self, quote):
        resp = self.actions.get_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_random_quote(self):
        resp = self.actions.get_random_quote()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_unidentified_quote(self):
        resp = self.actions.get_unidentified_quote()
        assert_valid_status_code(resp, 404)

    def test_get_quote_contributor(self, quote):
        resp = self.actions.get_quote_contributor(quote.id)
        assert_valid_status_code(resp, 401)

    def test_search_quotes(self, quote):
        resp = self.actions.search_quotes(quote.quotation)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
        assert_valid_search_results(resp, quote.quotation)
        assert resp.json['total'] >= 1

    def test_create_quote(self):
        resp = self.actions.create_quote()
        assert_valid_status_code(resp, 401)

    def test_update_quote(self, quote):
        resp = self.actions.update_quote(quote.id)
        assert_valid_status_code(resp, 401)

    def test_delete_quote(self, quote):
        resp = self.actions.delete_quote(quote.id)
        assert_valid_status_code(resp, 401)


class TestContributor:
    @pytest.fixture(autouse=True)
    def init(self, client, user):
        login(client, user)
        self.actions = Actions(client)

    def test_get_quotes(self):
        resp = self.actions.get_quotes()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_filter_quotes(self):
        pass

    def test_get_quote(self, quote):
        resp = self.actions.get_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_random_quote(self):
        resp = self.actions.get_random_quote()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_unidentified_quote(self):
        resp = self.actions.get_unidentified_quote()
        assert_valid_status_code(resp, 404)

    def test_get_quote_contributor(self, quote):
        resp = self.actions.get_quote_contributor(quote.id)
        assert_valid_status_code(resp, 403)

    def test_search_quotes(self, quote):
        resp = self.actions.search_quotes(quote.quotation)
        assert_valid_status_code(resp, 200)
        assert_valid_search_results(resp, quote.quotation)
        assert resp.json['total'] >= 1

    def test_create_quote(self):
        resp = self.actions.create_quote()
        assert_valid_status_code(resp, 201)
        assert_valid_schema(resp, 'quote.json')

    def test_update_quote(self, quote):
        resp = self.actions.update_quote(quote.id)
        assert_valid_status_code(resp, 403)

    def test_delete_quote(self, quote):
        resp = self.actions.delete_quote(quote.id)
        assert_valid_status_code(resp, 403)


class TestAdmin:
    @pytest.fixture(autouse=True)
    def init(self, client, user_admin):
        login(client, user_admin)
        self.actions = Actions(client)

    def test_get_quotes(self):
        resp = self.actions.get_quotes()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_filter_quotes(self):
        pass

    def test_get_quote(self, quote):
        resp = self.actions.get_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_random_quote(self):
        resp = self.actions.get_random_quote()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_get_unidentified_quote(self):
        resp = self.actions.get_unidentified_quote()
        assert_valid_status_code(resp, 404)

    def test_get_quote_contributor(self, quote):
        resp = self.actions.get_quote_contributor(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')

    def test_search_quotes(self, quote):
        resp = self.actions.search_quotes(quote.quotation)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
        assert_valid_search_results(resp, quote.quotation)
        assert resp.json['total'] >= 1

    def test_create_quote(self):
        resp = self.actions.create_quote()
        assert_valid_status_code(resp, 201)
        assert_valid_schema(resp, 'quote.json')

    def test_update_quote(self, quote):
        resp = self.actions.update_quote(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

    def test_delete_quote(self, quote):
        resp = self.actions.delete_quote(quote.id)
        assert_valid_status_code(resp, 204)
