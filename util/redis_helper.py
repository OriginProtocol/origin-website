import os
from redis import Redis, BlockingConnectionPool

def init_redis():
  global redis_client
  redis_client = Redis(
    connection_pool=BlockingConnectionPool(max_connections=20),
  ).from_url(os.environ.get("REDISCLOUD_URL"))

def get_redis_client():
  return redis_client
