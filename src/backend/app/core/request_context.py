from typing import Any, Dict, Optional


class RequestContext:
    """Request context for storing request-specific data"""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        """Set a value in the context"""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the context"""
        return self._data.get(key, default)

    def clear(self):
        """Clear all context data"""
        self._data.clear()
