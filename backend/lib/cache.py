"""
Cache backend abstraction layer.
Provides MockRedis for development and real Redis for production.
Both implement the same interface for seamless switching.
"""


class MockRedis:
    """
    In-memory mock Redis implementation for development.
    Implements common Redis methods with dict-backed storage.
    """

    def __init__(self):
        self._data = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value) -> None:
        self._data[key] = str(value)

    def incr(self, key: str) -> int:
        val = int(self._data.get(key, 0))
        new_val = val + 1
        self._data[key] = str(new_val)
        return new_val

    def decr(self, key: str) -> int:
        val = int(self._data.get(key, 0))
        new_val = val - 1
        self._data[key] = str(new_val)
        return new_val

    def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                deleted += 1
        return deleted

    def exists(self, key: str) -> bool:
        return key in self._data

    def clear(self) -> None:
        self._data.clear()
