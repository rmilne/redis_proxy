import pytest
import redis
import requests

# monkey patching requests to fix a timeout issue when the server address does not resolve
old_send = requests.Session.send
def new_send(*args, **kwargs):
     if kwargs.get("timeout", None) is None:
         kwargs["timeout"] = 5
     return old_send(*args, **kwargs)
requests.Session.send = new_send

def test_test():
    assert True == True

def test_request():
    r = requests.get('http://app:8080/key', timeout=5)
    assert r.status_code == 404

