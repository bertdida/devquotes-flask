from .test_auth import login
from .utils.assertions import (
    assert_valid_schema,
    assert_valid_status_code
)


class Actions:

    def __init__(self, client, quote):
        self.client = client
        self.quote = quote

    def like(self):
        post_data = {'id': self.quote.id}
        return self.client.post('/v1/likes', data=post_data)

    def unlike(self):
        return self.client.delete(f'/v1/likes/{self.quote.id}')

    def get_favorites(self):
        return self.client.get('/v1/likes')


def test_guest_user(client, quote):
    test = Actions(client, quote)

    resp = test.like()
    assert_valid_status_code(resp, 401)

    resp = test.unlike()
    assert_valid_status_code(resp, 401)

    resp = test.get_favorites()
    assert_valid_status_code(resp, 401)


def test_user(client, quote, user):
    login(client, user)
    test = Actions(client, quote)

    resp = test.like()
    assert_valid_status_code(resp, 200)
    assert_valid_schema(resp, 'quote.json')
    assert resp.json['data']['total_likes'] == 1

    resp = test.get_favorites()
    assert_valid_status_code(resp, 200)
    assert_valid_schema(resp, 'quotes.json')
    assert resp.json['total'] == 1

    resp = test.unlike()
    assert_valid_status_code(resp, 200)
    assert_valid_schema(resp, 'quote.json')
    assert resp.json['data']['total_likes'] == 0

    resp = test.get_favorites()
    assert resp.json['total'] == 0
