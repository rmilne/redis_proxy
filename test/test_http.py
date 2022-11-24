import os
import pytest
import requests


@pytest.mark.parametrize("env", [dict(**os.environ)])
def test_404(server):
    r = requests.get("http://127.0.0.1:8080/key4040404", timeout=5)
    assert r is not None
    assert r.status_code == 404


@pytest.mark.parametrize("env", [dict(**os.environ)])
def test_cache(server, _redis):
    _redis.set("cache_test", "cache_test")
    r = requests.get("http://127.0.0.1:8080/cache_test", timeout=5)
    assert r.status_code == 200
    assert r.text == "cache_test"
