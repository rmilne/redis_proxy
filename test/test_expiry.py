import os
import pytest
import time


@pytest.mark.parametrize('env', [dict(**os.environ, RP_CACHE_TIMEOUT='1')])
def test_cache_expiry(server, _redis, get):
    _redis.set('expiry_test', 'before')
    #    r = requests.get(f'http://127.0.0.1:8080/{}', timeout=5)
    val = get('expiry_test')
    assert get('expiry_test') == 'before'
    _redis.set('expiry_test', 'after')
    assert get('expiry_test') == 'before'
    time.sleep(1)
    assert get('expiry_test') == 'after'