
# TODO - add parsing to init

class Config():
    def __init__(self) -> None:
        self.server_address = None
        self.port = None
        self.redis_host = None
        self.redis_port = None
        self.cache_size = None
        self.cache_timeout = None