from .test_auth import login
from .utils.assertions import assert_valid_schema


class TestLike:

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


def test_unauthorized_user(client, quote):
    test = TestLike(client, quote)

    resp = test.like()
    assert resp.status_code == 401

    resp = test.unlike()
    assert resp.status_code == 401

    resp = test.get_favorites()
    assert resp.status_code == 401


def test_uthorized_user(client, quote, user):
    login(client, user)
    test = TestLike(client, quote)

    resp = test.like()
    assert resp.status_code == 200
    assert resp.json['data']['total_likes'] == 1
    assert_valid_schema(resp.json, 'quote.json')

    resp = test.get_favorites()
    assert resp.status_code == 200
    assert resp.json['total'] == 1
    assert_valid_schema(resp.json, 'quotes.json')

    resp = test.unlike()
    assert resp.status_code == 200
    assert resp.json['data']['total_likes'] == 0
    assert_valid_schema(resp.json, 'quote.json')

    resp = test.get_favorites()
    assert resp.json['total'] == 0
