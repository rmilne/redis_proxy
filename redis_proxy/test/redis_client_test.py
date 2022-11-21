import pytest

from ..__main__ import RedisProxy
from ..config import Config

@pytest.fixture
def proxy() -> RedisProxy:
    conf = Config()
    conf.server_address = '0.0.0.0'
    conf.port = 8080
    return RedisProxy(conf)

def test_parse_get_request(proxy: RedisProxy):
    request = "GET /the_key HTTP/1.1\r\n\r\n"
    assert proxy.parse_get_request(request) == "the_key"

def test_is_http(proxy: RedisProxy):
    redis_request = "GET the_key\r\n\r\n"
    http_request = "GET /the_key HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n"
    assert proxy.is_http(redis_request) == False
    assert proxy.is_http(http_request) == True

