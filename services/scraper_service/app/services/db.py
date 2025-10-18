from typing import Dict, Any


class Database:
    def __init__(self, character_name: str):
        self._character_name = character_name
        self.character_data: Dict = {}

    def get_character_name(self):
        return self._character_name

    def set_character_data(self, entry: Dict):
        self.character_data.update(entry)

