import cachetools
import logging

from redis_proxy.redis_client import RedisClient

log = logging.getLogger()

class RedisCacheManager():
    def __init__(self, config) -> None:
        self.cache = cachetools.TTLCache(maxsize=config.cache_size, ttl=config.cache_timeout)
        self.redis = RedisClient(config)
    
    def get(self, key: str) -> bytes:
        value = self.cache.get(key, None)
        if value is None:
            log.debug(f"cache miss for: {key}")
            value = self._get_from_redis(key)
        if value is not None:
            self.cache[key] = value
        return value

    def _get_from_redis(self, key: str) -> bytes:
        return self.redis.get(key)

    