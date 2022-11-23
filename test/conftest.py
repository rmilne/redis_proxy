import os
import pytest
import redis
import requests
import time

from subprocess import Popen, PIPE


@pytest.fixture
def server(env):
    p = Popen(["python3", "-m", "redis_proxy"], env=env, stdout=PIPE, stderr=PIPE)
    time.sleep(0.7)
    yield p
    p.kill()
    p.terminate()

@pytest.fixture
def _redis():
    host = os.environ.get('RP_REDIS_HOST', '127.0.0.1')
    r = redis.Redis(host)
    yield r
    r.close()

@pytest.fixture
def get():
    def inner_get(key):
        r = requests.get(f'http://127.0.0.1:8080/{key}', timeout=5)
        return r.text
    return inner_get