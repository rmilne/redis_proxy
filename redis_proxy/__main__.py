import asyncio
import logging
import sys

from typing import Optional

from .config import Config
from .cache import RedisCacheManager

log = logging.getLogger()

NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"

class RedisProxy():
    def __init__(self, config: Config) -> None:
        self.config = config
        self.manager = RedisCacheManager(config)

    def is_http(self, request: str) -> bool:
        token = request.split(maxsplit=3)
        if len(token) != 4 or not token[2].startswith('HTTP'):
            return False
        return True

    def parse_get_request(self, request: str) -> Optional[str]:
        tokens = request.split(' ')
        if tokens[0] != 'GET' or len(tokens) < 2:
            # invalid request
            return
        # return the key, strip the leading /
        return tokens[1][1:]

    async def request_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # TODO just read GET - decide what to do after.
        data = await reader.readuntil(bytes("\r\n\r\n", encoding='ascii'))
        request = data.decode()
        log.debug(f"request: >{repr(request)}<")

        key = self.parse_get_request(request)
        if key:
            value = self.manager.get(key)
            if value:
                value_str = str(value.decode('utf-8'))
                response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(value_str)}\r\n\r\n{value_str}\r\n"
            else:
                response = NOT_FOUND
        else:
            response = NOT_FOUND

        # respond
        writer.write(bytes(response, encoding='ascii'))
        await writer.drain()
        log.debug(f"responded: {repr(response)}")
        writer.close()

        return response

    async def run_server(self):
        server = await asyncio.start_server(self.request_handler, self.config.server_address, self.config.port)
        # TODO log details
        log.info(f"Started server on {self.config.server_address}:{self.config.port}")
        async with server:
            await server.serve_forever()

def main():
    # Parse config
    # TODO argparse or config file
    conf = Config()
    conf.server_address = '0.0.0.0'
    conf.port = 8080
    conf.redis_host = 'localhost'
    conf.redis_port = 6379
    conf.cache_size = 128
    conf.cache_timeout = 60

    # Setup logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Start server
    proxy = RedisProxy(conf)
    asyncio.run(proxy.run_server())



if __name__ == '__main__':
    main()