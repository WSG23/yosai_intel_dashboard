"""In-memory CSV storage placeholder"""

class CSVStorageRepository:
    def __init__(self, path: str) -> None:
        self.path = path
        self.sessions = {}

    def initialize(self) -> bool:
        return True

    def store_session_data(self, session_id: str, data):
        self.sessions[session_id] = data

    def get_session_data(self, session_id: str):
        return self.sessions.get(session_id)
