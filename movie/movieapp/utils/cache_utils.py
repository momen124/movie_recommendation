import redis
from django.conf import settings
from django.core.cache import cache

class RedisCache:
      def __init__(self):
          self.client = redis.Redis(
              host=settings.REDIS_HOST,
              port=settings.REDIS_PORT,
              db=settings.REDIS_DB
          )

      def set_cache(self, key, value, timeout=3600):
          cache.set(key, value, timeout)

      def get_cache(self, key):
          return cache.get(key)

      def delete_cache(self, key):
          cache.delete(key)

cache_instance = RedisCache()