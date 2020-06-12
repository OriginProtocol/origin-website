import os
from redis import Redis

def init_redis():
  global redis_client
  redis_client = Redis.from_url(os.environ['REDIS_URL'])
