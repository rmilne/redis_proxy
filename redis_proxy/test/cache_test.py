import cachetools
import pytest
import unittest

from collections import defaultdict
from unittest.mock import patch

from redis_proxy.cache import RedisCacheManager

class TestingRedisCacheManager(RedisCacheManager):
    __test__ = False
    def __init__(self, ddict: defaultdict, size: float, ttl: float):
        self.cache = cachetools.TTLCache(maxsize=size, ttl=ttl)
        self.redis = ddict
    

def test_cache_manager_cache_get():
    redis = defaultdict(None)
    redis['test'] = 'value'
    manager = TestingRedisCacheManager(redis, 10, 10)
    value = manager.get('test')
    assert value == 'value'
    manager.redis['test'] = 'not value'
    value = manager.get('test')
    assert value == 'value'
    




