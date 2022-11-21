import redis

from config import Config


class RedisClient():
    def __init__(self, config: Config):
        self.config = config
        self.redis = redis.Redis(host=config.redis_host, port=config.redis_port)

    def get(self, key: str) -> bytes:
        return self.redis.get(key)
