import os
import pytest
import requests


# monkey patching requests to fix a timeout issue when the server address does not resolve
old_send = requests.Session.send
def new_send(*args, **kwargs):
     if kwargs.get("timeout", None) is None:
         kwargs["timeout"] = 5
     return old_send(*args, **kwargs)
requests.Session.send = new_send

@pytest.mark.parametrize('env', [dict(**os.environ)])
def test_404(server):
    r = None
    try:
        r = requests.get('http://127.0.0.1:8080/key4040404', timeout=5)
    except Exception as e:
        r = None
        print(e)
    assert r is not None
    assert r.status_code == 404


@pytest.mark.parametrize('env', [dict(**os.environ)])
def test_cache(server, _redis):
    _redis.set('cache_test', 'cache_test')
    r = requests.get('http://127.0.0.1:8080/cache_test', timeout=5)
    assert r.status_code == 200
    assert r.text == "cache_test"