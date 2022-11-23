import os
import pytest

@pytest.mark.parametrize('env', [dict(**os.environ, RP_CACHE_SIZE='2')])
def test_lru_eviction(server, _redis, get):
    for x in range(3):
        k = f'lru_{x}'
        v = str(x)
        _redis.set(k, v)
        assert get(k) == v
    # cache has 1, 2, not 0:  2 evicted 0 when it was retrieved

    # loop in reverse to leave 2, 1 in place and then check for 'evicted' for 0
    # set all as evicted in redis
    for x in range(2, -1, -1):
        k = f'lru_{x}'
        v = 'evicted'
        _redis.set(k, v)
        if x == 0:
            # 0 will return evicted becase it had been evicted
            assert get(k) == v
        else:
            assert get(k) == str(x)