Redis Proxy Service
===================

## High level architecture

This service acts as a caching layer in front of Redis. 

`redis_proxy` will:
 
1. Accept  HTTP or Redis `GET` requests for a simple `key`
1. Check its local cache for the `key` to retrieve the `value`
1. In the case of a cache miss: retrieve the `value` from its backing Redis instance and populate the local cache
1. Return the value in the response

`redis_proxy` is implemented with Python and has 3 main features:

1. TCP Server built with [asyncio](https://docs.python.org/3/library/asyncio.html), which provides an event loop to process connections concurrently with an async/await syntax.
1. [TTLCache](https://cachetools.readthedocs.io/en/latest/#cachetools.TTLCache) provided by the [cachetools](https://github.com/tkem/cachetools) package, which has Least Recently Used (LRU) behaviour.
1. Pool of processes that connect to Redis in parallel, using [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) and the [Redis](https://redis.io/) client [library](https://github.com/redis/redis-py)

## Prerequisites:

- docker
- docker-compose
- make

Tested on Windows WSL2, MacOS, Linux

## Usage:

```
git clone https://github.com/rmilne/redis_proxy.git
cd redis_proxy
make test
```

#### Configuration:

Configuration is using a combination of environment variables that can be overwritten by command line arguments:

Environment Variables:
```
RP_LISTEN_ADDRESS
RP_PORT
RP_REDIS_HOST
RP_REDIS_PORT
RP_CACHE_SIZE
RP_CACHE_TIMEOUT
RP_CLIENT_LIMIT
```

Command line arguments:
```
> python -m redis_proxy -h
usage: python -m redis_proxy [-h] [--listen-address LISTEN_ADDRESS] [--port PORT] [--redis-host REDIS_HOST] [--redis-port REDIS_PORT] [--cache-size CACHE_SIZE] [--cache-timeout CACHE_TIMEOUT] [--client-limit CLIENT_LIMIT]

redis_proxy

optional arguments:
  -h, --help            show this help message and exit
  --listen-address LISTEN_ADDRESS
  --port PORT
  --redis-host REDIS_HOST
  --redis-port REDIS_PORT
  --cache-size CACHE_SIZE
  --cache-timeout CACHE_TIMEOUT
  --client-limit CLIENT_LIMIT
  ```


## Code design

### Libraries chosen
Python 3:
 - [asyncio](https://docs.python.org/3/library/asyncio.html)
 - [cachetools](https://github.com/tkem/cachetools)
 - [redis-py](https://github.com/redis/redis-py)
 - [pytest](https://docs.pytest.org/en/7.2.x/)

### Requirements and design choices


#### TCP Server:
The combination of requirements involving concurrency, HTTP/Redis protocols, and parallel cache retrieval led me towards an asynchronous event loop design.  Event loops excel at I/O blocking workloads that require a high level of concurrency and speed. Python frameworks such as Twisted, Tornado, and python3's asyncio were considered.  The asyncio library was chosen for its simplicity and also the freedom to accommodate 2 protocols without much complexity.

#### HTTP and Redis protocol handling

The service supports HTTP/1.1 GET requests and Redis GET requests on the same listening port.  A simple protocol detection selects which protocol to parse and respond with.

An example HTTP GET to retrieve the key `Rescale` would look like this:
```
# This produces a request that starts with:  'GET /Rescale HTTP/1.1'
> curl http://host:port/Rescale
We Accelerate Engineering Breakthroughs
```

The `redis-cli` example:

```
# This produces request string: '*2\r\n$3\r\nget\r\n$7\r\nRescale\r\n'
> redis-cli -p 8080 get Rescale
"We Accelerate Engineering Breakthroughs"
```

#### Local cache
The local cache is required to operate with a Least Recently Used (LRU) policy, global expiry or Time To Live (TTL), and a fixed maximum size.  Developing this cache is straightforward but well tested libraries like the [functools @lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) and [cachetools](https://github.com/tkem/cachetools) exist.  The [cachetools](https://github.com/tkem/cachetools) implementation was picked due to convenience and compatibility with asyncio python functions.

TTLCache is very simple to use:

```python
cache = cachetools.TTLCache(maxsize=config.cache_size, ttl=config.cache_timeout)
# set
cache[key] = value
# get
cached_value = cache[key]
# get with default value None
cached_value = cache.get(key, None)
```

#### Redis workers

The [redis-py](https://github.com/redis/redis-py) library was the obvious choice to connect to the Redis datastore.  It is also simple:

```python
import redis

client = redis.Redis(host)
value = client.get(key)
```

#### Parallel concurrency

The bonus requirement of `parallel concurrency` led me to wonder if asyncio is an acceptable solution as event loops are `concurrent` but not `parallel`, as explained in this [article](https://medium.com/@itIsMadhavan/concurrency-vs-parallelism-a-brief-review-b337c8dac350).  Only separate processes are truly parallel in Python because the Global Interpreter Lock (GIL) disqualifies Python threads.  A ProcessPool was used to allow each redis client to have their own parallel execution environment, but I suspect that this may be less performant than using asyncio here as well.   The workload is I/O intensive, not CPU intensive and multiple processes have a communication (IPC) overhead to send results back to the cache.  The shared local cache would also suffer if it were shared between the process pool, so leaving it in the single threaded portion of the server was best.

#### Implementation assumptions and limitations

For simplicity there are some assumptions made in the implementation details:

- Only URL safe characters are supported for the HTTP protocol handling
   - (redis itself supports spaces among other special characters)
- The redis protocol is not robustly parsed, just enough to parse 2 forms of `GET`
- Protocol validation is not robust for HTTP or Redis

#### Testing

Integration tests are located: `redis_proxy/test`
Unit tests are located: `redis_proxy/redis_proxy/test`

## Complexity

With Redis the time complexity of the [`GET`](https://redis.io/commands/get/) and [`SET`](https://redis.io/commands/set/) commands is O(1).

The cache, in [cachetools.TTLCache](https://github.com/tkem/cachetools/blob/master/src/cachetools/__init__.py#L373), is implemented with an `OrderedDict` and does doubly linked list manipulations.  Python's implementation has a complexity of O(1) for get, set, and delete operations. The author of Python's caching libraries has weighed in on conversations on this [topic](https://stackoverflow.com/a/8177061).

Generally this service is O(1).


## Time spent

Development time was spread over 4 days, with lots of learning and research up front

- 4h :  Research into libraries and frameworks that were 100% new to me (Tornado, Twisted, asyncio, functools.lru_cache, cachetools, asyncio & multiprocessing pools)
- 4h :  Learning how to work with and pytest asyncio, it is a different style
- 1h :  Basic web server, local cache and redis client
- 2h :  Makefile, Dockerfile, docker-compose setup
- 2h :  running subprocess of redis_proxy under pytest
- 2h :  adding parallel workers
- 1h :  adding the redis protocol support
- 3h :  Writing this readme

These times are approximate and also reflect some extra time spent learning.

## Requirements not implemented

N/A

## Bugs, TODOs, Concerns, Best laid plans

A candid list of things that are not neat and tidy about this project.

TODO:
- unittest coverage is incomplete, integration testing superseded that effort
- Type-hinting is incomplete, integrating a type checking tool like [mypy](https://mypy.readthedocs.io/en/stable/index.html) would help
- Python docstrings and auto-generated documentation
- CI/CD with github actions, linting + type checking steps, docker deployment
- benchmarking a purely asyncio solution without multiprocessing workers

Concerns:
- large redis values (>100000 characters) seem to fail when requesting them with python requests and http.client libraries, there may be an issue with how I've implemented the server
- testing parallel concurrency is challenging, depending on the host the timing of worker processing is inconsistent
- I had hoped to follow TDD, but test setup added a lot of up-front friction.  Exploratory development took precedence

Artifacts:

- my [trello](https://trello.com/b/JJF4N1CP/rescale-redis-proxy-project) to track my tasks was helpful, but isn't an actively useful project artifact
