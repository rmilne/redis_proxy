import http.client
import os
import pytest
import redis
import socket
import time

from subprocess import Popen, PIPE


@pytest.fixture
def server(env):
    p = Popen(["python3", "-m", "redis_proxy"], env=env, stdout=PIPE, stderr=PIPE)
    # wait for the server to start up, 0.5 seconds,
    # then start hitting the port to see if the socket is open
    time.sleep(0.5)
    found = False
    count = 0
    while not found and count < 100:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(("127.0.0.1", 8080))
            found = True
            sock.close()
        except:
            time.sleep(0.1)
        count += 1
    # a little extra padding time
    time.sleep(0.2)
    yield p
    p.kill()
    p.terminate()


@pytest.fixture
def _redis():
    host = os.environ.get("RP_REDIS_HOST", "127.0.0.1")
    r = redis.Redis(host)
    yield r
    r.close()


@pytest.fixture
def get():
    def inner_get(key):
        conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=20)
        conn.request("GET", f"/{key}")
        resp = conn.getresponse()
        data = resp.read().decode("utf-8")
        return data

    return inner_get
