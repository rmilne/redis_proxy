import argparse
import os


class Config:
    def __init__(self) -> None:
        self.server_address = None
        self.port = None
        self.redis_host = None
        self.redis_port = None
        self.cache_size = None
        self.cache_timeout = None
        self.client_limit = None

    def parse(self, *arg, **kwargs):
        parser = argparse.ArgumentParser(description="redis_proxy")
        parser.add_argument(
            "--listen-address", default=os.environ.get("RP_LISTEN_ADDRESS", "0.0.0.0")
        )
        parser.add_argument("--port", default=os.environ.get("RP_PORT", 8080), type=int)
        parser.add_argument(
            "--redis-host", default=os.environ.get("RP_REDIS_HOST", "127.0.0.1")
        )
        parser.add_argument(
            "--redis-port", default=os.environ.get("RP_REDIS_PORT", 6379), type=int
        )
        parser.add_argument(
            "--cache-size", default=os.environ.get("RP_CACHE_SIZE", 32), type=int
        )
        parser.add_argument(
            "--cache-timeout", default=os.environ.get("RP_CACHE_TIMEOUT", 30), type=int
        )
        parser.add_argument(
            "--client-limit", default=os.environ.get("RP_CLIENT_LIMIT", 8), type=int
        )
        args = parser.parse_args()
        self.server_address = args.listen_address
        self.port = args.port
        self.redis_host = args.redis_host
        self.redis_port = args.redis_port
        self.cache_size = args.cache_size
        self.cache_timeout = args.cache_timeout
        self.client_limit = args.client_limit
