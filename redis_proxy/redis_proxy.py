import asyncio
import logging
import sys

from typing import Optional

log = logging.getLogger()


class Config():
    # TODO - replace with conf parsing object
    pass


def is_http(request: str) -> bool:
    return True

def parse_get_request(request: str) -> Optional[str]:
    tokens = request.split(' ')
    if tokens[0] != 'GET' or len(tokens) < 2:
        # invalid request
        return
    # return the key, strip the leading /
    return tokens[1][1:]

async def request_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # TODO just read GET - decide what to do after.
    data = await reader.readuntil(bytes("\r\n\r\n", encoding='ascii'))
    request = data.decode()
    log.debug(f"request: >{request}<")

    
    # TODO WORK
    key = parse_get_request(request)

    response = f"HTTP/1.1 200 OK\r\n\r\nkey: {key}"

    # respond
    writer.write(bytes(response, encoding='ascii'))
    await writer.drain()
    log.debug(f"responded: {response}")
    writer.close()

    return response

async def run_server(conf: Config):
    server = await asyncio.start_server(request_handler, conf.server_address, conf.port)
    # TODO log details
    log.info(f"Started server on {conf.server_address}:{conf.port}")
    async with server:
        await server.serve_forever()

def main():
    # Parse config
    # TODO argparse or config file
    conf = Config()
    conf.server_address = '0.0.0.0'
    conf.port = 8080
    # Setup logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # Start server
    asyncio.run(run_server(conf))



if __name__ == '__main__':
    main()