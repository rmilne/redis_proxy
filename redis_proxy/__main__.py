import asyncio
import logging
import sys

from typing import Optional

from .config import Config
from .cache import RedisCacheManager

log = logging.getLogger()

NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
SERVICE_UNAVAILABLE = "HTTP/1.1 503 Service Unavailable\r\n\r\n"


class RedisProxy:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.manager = RedisCacheManager(config)
        self._client_count = 0

    def is_http(self, request: str) -> bool:
        token = request.split(maxsplit=3)
        log.debug(f"http detect tokens: {token}")
        if token[0].upper() == "GET" and token[2].startswith("HTTP"):
            return True
        return False

    def is_redis(self, request: str) -> bool:
        if request.startswith("*") and request.endswith("\r\n"):
            return True
        return False

    async def parse_redis_get(
        self, request: str, reader: asyncio.StreamReader
    ) -> tuple:
        lines = [request]
        # strip * and /r/n to get length of array
        array_len = int(request[1:].strip())

        for x in range(array_len * 2):
            line = await reader.readline()
            lines.append(line.decode())
            log.debug(f"readline: {line}")
        log.debug(f"full request: {repr(''.join(lines))}")

        if array_len == 1:
            line = lines[2]
            key = line.strip()
            log.debug(f"key {key}")
        elif array_len == 2:
            # could check for 'GET' here for further validation
            line = lines[4]
            key = line.strip()
            log.debug(f"key {key}")
        else:
            log.debug(f"invalid array len {array_len}")
            key = None

        return key

    def parse_http_get(self, request: str):
        tokens = request.split(" ")
        if tokens[0] != "GET" or len(tokens) < 2:
            # invalid request
            log.debug(f"invalid get request: {request}")
            return None
        # return the key, strip the leading /
        log.debug(f"found key: {tokens[1][1:]}")
        return tokens[1][1:]

    async def parse_get_request(self, reader: asyncio.StreamReader) -> Optional[tuple]:
        first_line = await reader.readuntil(bytes("\n", encoding="utf-8"))
        request = first_line.decode()
        log.debug(f"first request line: >{repr(request)}<")
        if self.is_http(request):
            log.debug("http detected")
            key = self.parse_http_get(request)
            return True, key
        elif self.is_redis(request):
            log.debug("redis detected")
            key = await self.parse_redis_get(request, reader)
            return False, key
        else:
            # invalid request
            log.debug("did not detect http or redis")
            return True, None

    def redis_response(self, value: Optional[str]) -> str:
        # not found: $-1
        if value is not None:
            resp = f"${len(value)}\r\n{value}\r\n"
        else:
            resp = f"$-1\r\n"
        return resp

    async def request_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        # track client count
        ishttp = True
        self._client_count += 1
        try:
            if self.config.client_limit < self._client_count:
                response = SERVICE_UNAVAILABLE
            else:
                ishttp, key = await self.parse_get_request(reader)
                if key is not None:
                    value = await self.manager.get(key)
                    if not ishttp:
                        response = self.redis_response(value)
                    else:
                        if value:
                            if ishttp:
                                response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(value)}\r\n\r\n{value}"
                            else:
                                response = self.redis_response(value)
                        else:
                            response = NOT_FOUND
                else:
                    response = NOT_FOUND
                    if not ishttp:
                        response = self.redis_response(None)

            # respond
            writer.write(bytes(response, encoding="utf-8"))
            await writer.drain()
            log.debug(f"responded: {repr(response)}")
            writer.close()
        except Exception as e:
            raise e
        finally:
            # track client count
            self._client_count -= 1

        return response

    async def run_server(self):
        log.debug("Starting server...")
        server = await asyncio.start_server(
            self.request_handler, self.config.server_address, self.config.port
        )
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


if __name__ == "__main__":
    main()
