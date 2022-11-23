import asyncio
import cachetools
import pytest
import unittest

from collections import defaultdict
from unittest.mock import patch

from redis_proxy.cache import RedisCacheManager
from redis_proxy.config import Config

class TestingRedisCacheManager(RedisCacheManager):
    __test__ = False
    def __init__(self, ddict: defaultdict, size: float, ttl: float):
        self.cache = cachetools.TTLCache(maxsize=size, ttl=ttl)
        self.redis = ddict
        self.config = Config()
        self.config.client_limit = 1
    
    def _get_from_redis(self, key: str) -> bytes:
        return self.redis.get(key, None)
    
@pytest.mark.asyncio
async def test_cache_manager_cache_get():
    redis = defaultdict(None)
    redis['test'] = 'value'
    manager = TestingRedisCacheManager(redis, 10, 10)
    value = await manager.get('test')
    assert value == 'value'
    manager.redis['test'] = 'not value'
    value = await manager.get('test')
    assert value == 'value'
    




