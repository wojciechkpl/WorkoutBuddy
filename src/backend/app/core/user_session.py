from typing import Any, Dict, Optional


class UserSession:
    """User session for storing user-specific session data"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self.user_id: Optional[int] = None

    def set_user_id(self, user_id: int):
        """Set the current user ID"""
        self.user_id = user_id

    def get_user_id(self) -> Optional[int]:
        """Get the current user ID"""
        return self.user_id

    def set(self, key: str, value: Any):
        """Set a value in the session"""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the session"""
        return self._data.get(key, default)

    def clear(self):
        """Clear all session data"""
        self._data.clear()
        self.user_id = None
