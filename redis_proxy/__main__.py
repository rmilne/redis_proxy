import asyncio
import logging
import sys

from typing import Optional

from .config import Config
from .cache import RedisCacheManager

log = logging.getLogger()

NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
SERVICE_UNAVAILABLE = "HTTP/1.1 503 Service Unavailable\r\n\r\n"

class RedisProxy():
    def __init__(self, config: Config) -> None:
        self.config = config
        self.manager = RedisCacheManager(config)
        self._client_count = 0

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
        # track client count
        self._client_count += 1
        if self.config.client_limit < self._client_count:
            response = SERVICE_UNAVAILABLE
        else:
            data = await reader.readuntil(bytes("\r\n\r\n", encoding='ascii'))
            request = data.decode()
            log.debug(f"request: >{repr(request)}<")

            key = self.parse_get_request(request)
            if key:
                value = await self.manager.get(key)
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
        # track client count
        self._client_count -= 1
        return response

    async def run_server(self):
        log.debug("Starting server...")
        server = await asyncio.start_server(self.request_handler, self.config.server_address, self.config.port)
        # TODO log details
        log.info(f"Started server on {self.config.server_address}:{self.config.port}")
        async with server:
            await server.serve_forever()

def main():
    # Parse config
    conf = Config()
    conf.parse(*sys.argv[1:])

    # Setup logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Start server
    proxy = RedisProxy(conf)
    asyncio.run(proxy.run_server())



if __name__ == '__main__':
    main()