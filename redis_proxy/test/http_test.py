import asyncio
import pytest
import socket

import redis_proxy.redis_proxy as redis_proxy

@pytest.fixture
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_parse_get_request():
    request = "GET /the_key HTTP/1.1\r\n\r\n"
    assert redis_proxy.parse_get_request(request) == "the_key"
