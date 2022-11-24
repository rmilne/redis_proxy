import http.client
import os
import multiprocessing
import requests
import socket
import time

import pytest


def is_closed(sock):
    try:
        buf = sock.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT)
        if buf == b"":
            return True
    except:
        pass
    return False


@pytest.mark.parametrize("env", [dict(**os.environ, RP_CLIENT_LIMIT="12")])
def test_concurrent_connections(server, _redis, get):
    clients = []
    n = 8
    for x in range(n):
        _redis.set(x, x)
        clients.append(http.client.HTTPConnection("127.0.0.1", 8080))

    # all are connected at the same time
    for conn in clients:
        assert is_closed(conn.sock) == False

    # all requesting data
    for i, conn in enumerate(clients):
        conn.request("GET", f"/{i}")
        resp = conn.getresponse()
        assert resp.status == 200
        assert resp.read().decode("utf-8") == str(i)

    for conn in clients:
        conn.close()


def safe_get(key):
    conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=20)
    conn.request("GET", f"/{key}")
    resp = conn.getresponse()
    return resp.status


@pytest.mark.parametrize("env", [dict(**os.environ, RP_CLIENT_LIMIT="4")])
def test_concurrent_client_limit(server, _redis, get):
    clients = []
    n = 8

    for x in range(n):
        _redis.set(x, f"{x}" * 10000)  # set large keys

    with multiprocessing.Pool(n) as p:
        codes = p.map(safe_get, [str(x) for x in range(n)])

    two_hundreds = codes.count(200)
    error_count = codes.count(503)
    assert two_hundreds >= 4
    assert error_count > 0


def concurrent_get(queue, key):
    conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=10)
    conn.request("GET", f"/{key}")
    resp = conn.getresponse()
    # value = resp.read().decode('utf-8')
    queue.put(key)
    conn.close()


@pytest.mark.parametrize("env", [dict(**os.environ, RP_CLIENT_LIMIT="30")])
def test_concurrent_work(server, _redis, get):
    clients = []
    n = 8
    m = multiprocessing.Manager()
    results = m.Queue()

    for x in range(n):
        if x < (n / 2):
            strlen = 10000
            _redis.set(x, f"{x}" * strlen)  # set large keys for half
        else:
            strlen = 1
            _redis.set(x, f"{x}" * strlen)
            # warm the cache
            get(x)

    with multiprocessing.Pool(n) as p:
        p.starmap(concurrent_get, [(results, str(x)) for x in range(n)])

    order = []
    for x in range(n):
        order.append(int(results.get(timeout=5)))

    # test at least 2 of the 0,1,2,3 positions are >= 4
    # proving that the faster work finishes first even though they were started second
    fast_keys = 0
    for i in range(n):
        if i < 4:
            if order[i] >= 4:
                fast_keys += 1
    assert fast_keys > 1
