import json
from typing import List, Dict


class UserHistoryService:
    def __init__(self, user_history_doc_path: str, user_history_query_path: str):
        self.user_history_doc = self.load_json(user_history_doc_path)
        self.user_history_query = self.load_json(user_history_query_path)

    def load_json(self, file_path: str) -> Dict:
        with open(file_path, "r") as f:
            return json.load(f)

    def get_user_history_doc(self, name: str) -> Dict:
        return self.user_history_doc.get(name, {})

    def get_user_history_query(self, name: str) -> Dict:
        return self.user_history_query.get(name, {})

    def get_user_history(self, name: str) -> Dict:
        return (
            self.get_user_history_doc(name),
            self.get_user_history_query(name),
        )
