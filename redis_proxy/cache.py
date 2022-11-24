import asyncio
import cachetools
import logging

from concurrent.futures import ProcessPoolExecutor
from redis_proxy.redis_client import RedisClient

log = logging.getLogger()

class RedisCacheManager():
    def __init__(self, config) -> None:
        self.config = config
        self.cache = cachetools.TTLCache(maxsize=config.cache_size, ttl=config.cache_timeout)
    
    async def get(self, key: str) -> str:
        value = self.cache.get(key, None)
        if value is None:
            log.debug(f"cache miss for: {key}")
            with ProcessPoolExecutor(self.config.client_limit) as pool:
                loop = asyncio.get_event_loop()
                value = await loop.run_in_executor(pool, self._get_from_redis, key)
        if value is not None:
            # ensure a string type
            try:
                value = value.decode("utf-8")
            except Exception as e:
                pass
            self.cache[key] = value
        return value

    def _get_from_redis(self, key: str) -> bytes:
        redis = RedisClient(self.config)
        return redis.get(key)

    