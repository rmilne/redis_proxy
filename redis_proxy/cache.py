import cachetools

from redis_client import RedisClient


class RedisCacheManager():
    def __init__(self, config) -> None:
        self.cache = cachetools.TTLCache(maxsize=config.cache_size, ttl=config.cache_timeout)
        self.redis = RedisClient(config)
    
    def get(self, key: str) -> bytes:
        return self.get_from_redis(key)

    def get_from_redis(self, key: str) -> bytes:
        return self.redis.get(key)

    