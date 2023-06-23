import os
from urllib.parse import urlparse
from redis import Redis, BlockingConnectionPool

url = urlparse(os.environ.get("REDIS_URL"))

def init_redis():
  global redis_client
  redis_client = Redis(
    host=url.hostname,
    port=url.port,
    password=url.password,
    connection_pool=BlockingConnectionPool(max_connections=1),
    ssl=True, 
    ssl_cert_reqs=None
  )

def get_redis_client():
  return redis_client
