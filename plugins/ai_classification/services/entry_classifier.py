"""Placeholder entry classification service"""

from typing import List, Dict

from ..database.csv_storage import CSVStorageRepository
from ..config import EntryClassificationConfig


class EntryClassificationService:
    """Classify entry/exit records."""

    def __init__(self, repository: CSVStorageRepository, config: EntryClassificationConfig) -> None:
        self.repository = repository
        self.config = config

    def classify_entries(self, data: List[Dict], session_id: str) -> List[Dict]:
        # Very naive implementation: mark all as 'entry'
        classified = []
        for row in data:
            row_copy = dict(row)
            row_copy["classification"] = "entry"
            classified.append(row_copy)
        self.repository.store_entry_classification(session_id, classified)
        return classified

