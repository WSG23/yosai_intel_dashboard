"""In-memory CSV storage repository"""

from typing import Any, Dict, Optional


class CSVStorageRepository:
    def __init__(self, path: str) -> None:
        self.path = path
        self.sessions: Dict[str, Any] = {}

    def initialize(self) -> bool:
        return True

    def store_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        self.sessions[session_id] = data

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    # Column mapping
    def store_column_mapping(self, session_id: str, mapping: Dict[str, Any]) -> None:
        sess = self.sessions.setdefault(session_id, {})
        sess["column_mapping"] = mapping

    def update_column_mapping(self, session_id: str, mapping: Dict[str, Any]) -> None:
        sess = self.sessions.setdefault(session_id, {})
        sess["column_mapping"] = mapping

    def get_column_mapping(self, session_id: str) -> Optional[Dict[str, Any]]:
        sess = self.sessions.get(session_id)
        if sess:
            return sess.get("column_mapping")
        return None

    # Floor estimation
    def store_floor_estimation(self, session_id: str, data: Dict[str, Any]) -> None:
        sess = self.sessions.setdefault(session_id, {})
        sess["floor_estimation"] = data

    # Entry classification
    def store_entry_classification(self, session_id: str, data: Any) -> None:
        sess = self.sessions.setdefault(session_id, {})
        sess["entry_classification"] = data

    # Permanent storage (placeholder)
    def save_permanent_data(self, session_id: str, client_id: str) -> bool:
        return True

