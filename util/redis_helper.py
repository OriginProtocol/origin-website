import os
from redis import Redis, BlockingConnectionPool

def init_redis():
  global redis_client
  redis_client = Redis(connection_pool=BlockingConnectionPool(max_connections=1)).from_url(os.environ['REDIS_URL'])
def get_redis_client():
  return redis_client
