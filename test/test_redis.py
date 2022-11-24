import os
import pytest
import redis


@pytest.mark.parametrize("env", [dict(**os.environ)])
def test_redis_client(server, _redis, get):
    _redis.set("test", "redis protocol")
    # connect to the proxy, with the redis client
    proxy = redis.Redis(
        host=os.environ.get("RP_LISTEN_ADDRESS", "127.0.0.1"),
        port=os.environ.get("RP_PORT", 8080),
    )
    value = proxy.get("test")
    assert value.decode("utf-8") == "redis protocol"
