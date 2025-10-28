import json
from collections import Counter
from pathlib import Path
from typing import Set, List, Dict
from services.data_processor.textCleaner import TextCleaner

class DataInit:
    def __init__(self, character_name: str) -> None:
        self.ignore_words = self.get_ignore_words()
        self.words : Set[str] = set()
        self.words_counter : Counter[str] = Counter()
        self.result_stats : Dict = {}
        self.results : Dict = {}
        self.get_path : Dict = {}
        self.new_words : Set[str] = set()
        self.textProcessor = TextCleaner
        self.character_name = character_name

        self._create_result_database()

    def __str__(self):
        if not self.results: return "No results available."
        my_sep = "-" * 40; res = ""
        for key in self.results: res += f"{key}: {self.results[key]}" + f"\n{my_sep}\n\n"
        return res

    def _create_result_database(self) -> None:
        """
        Loads the database from a JSON file and initializes the paths to words.
        :return: None
        """
        file_path = Path(__file__).resolve().parent.parent / "data" / "stats.json"
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.result_stats = data
            self._find_words_path_in_db(data)

    def _find_words_path_in_db(self, data, paths_to_word: List[str] = None) -> None:
        """
        Recursively finds words in the database and records their paths.
        :param data: The current level of the database being processed.
        :param paths_to_word: The path taken to reach the current level.
        :return: None
        """
        if paths_to_word is None:
            paths_to_word = []
        for key in data:
            current_path = paths_to_word + [key]
            if isinstance(data[key], list):
                for word in data[key]:
                    if word not in self.get_path:
                        self.words.add(word)
                        self.get_path[word] = set()
                    self.get_path[word].add(tuple(current_path))
            elif isinstance(data[key], dict):
                self._find_words_path_in_db(data[key], current_path)

    @staticmethod
    def get_ignore_words() -> Set[str]:
        """
        Loads and returns a set of words to ignore from a JSON file.
        """
        file_path = Path(__file__).resolve().parent.parent / "data" / "ignore_words.json"
        with open(file_path, "r", encoding="utf-8") as file:
            return set(word.strip().lower() for word in json.load(file))

