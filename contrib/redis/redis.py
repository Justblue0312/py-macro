from collections.abc import MutableMapping
from threading import Lock

from orjson import dumps, loads
from redis import StrictRedis


class RedisStore(MutableMapping):
    def __init__(self, redis_url: str, key_prefix: str = ""):
        """
        Initializes the RedisStore object.

        Args:
            redis_url: The URL of the Redis server.
            key_prefix: Optional prefix for all keys stored in Redis.
        """
        self.redis = StrictRedis.from_url(redis_url)
        self.key_prefix = key_prefix
        self._lock = Lock()

    def __getitem__(self, key, default_value=None):
        """
        Gets the value associated with the given key.

        Args:
            key: The key to retrieve.

        Returns:
            The value associated with the key, or None if the key does not exist.
        """
        key = self._get_full_key(key)
        data = self.redis.get(key)
        return loads(data) if data else default_value

    def __setitem__(self, key, value):
        """
        Sets the value associated with the given key.

        Args:
            key: The key to set.
            value: The value to associate with the key.
        """
        with self._lock:
            key = self._get_full_key(key)
            value = dumps(value)
            self.redis.set(key, value)

    def __delitem__(self, key):
        """
        Deletes the key-value pair associated with the given key.

        Args:
            key: The key to delete.
        """
        with self._lock:
            key = self._get_full_key(key)
            self.redis.delete(key)

    def __iter__(self):
        """
        Iterates over all keys in the store.

        Returns:
            An iterator of keys.
        """
        pattern = self.key_prefix + "*"
        for key in self.redis.scan(match=pattern):
            yield key.decode()[len(self.key_prefix):]

    def __len__(self):
        """
        Returns the number of key-value pairs in the store.

        Returns:
            The number of key-value pairs.
        """
        pattern = self.key_prefix + "*"
        return len(list(self.redis.scan(match=pattern)))

    def _get_full_key(self, key):
        """
        Returns the full key with the prefix appended.

        Args:
            key: The key.

        Returns:
            The full key.
        """
        return f"{self.key_prefix}{key}"
