import asyncio
import logging
import sys

from typing import Optional

from .config import Config
from .cache import RedisCacheManager
from .proxy import RedisProxy


def main():
    # Parse config
    conf = Config()
    conf.parse(*sys.argv[1:])

    # Setup logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Start server
    redisproxy = RedisProxy(conf)
    asyncio.run(redisproxy.run_server())


if __name__ == "__main__":
    main()
