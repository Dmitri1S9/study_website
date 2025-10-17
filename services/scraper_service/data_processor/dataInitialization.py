import json
from collections import Counter
from typing import Set, List, Dict


class DataCollector:
    def __init__(self) -> None:
        self._ignore_words = self.get_ignore_words()
        self._words : Set[str] = set()
        self._words_counter : Counter[str] = Counter()
        self._database_new : Dict = {}
        self._results : Dict = {}
        self._get_path : Dict = {}
        self._new_words : Set[str] = set()

    def _create_result_database(self) -> None:
        """
        Loads the database from a JSON file and initializes the paths to words.
        :return: None
        """
        with open("data/stats.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            self._database_new = data
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
                    if word not in self._get_path:
                        self._words.add(word)
                        self._get_path[word] = set()
                    self._get_path[word].add(tuple(current_path))
            elif isinstance(data[key], dict):
                self._find_words_path_in_db(data[key], current_path)

    @staticmethod
    def get_ignore_words() -> Set[str]:
        """
        Loads and returns a set of words to ignore from a JSON file.
        """
        with open("data/ignore_words.json", "r", encoding="utf-8") as file:
            return set(word.strip().lower() for word in json.load(file))

    def set_new_ignore_word(self, new_words: Set[str]) -> None:
        """
        Adds new words to the ignore words list and saves them to the JSON file.
        """
        ignore_words = self.get_ignore_words()
        ignore_words.update(word.strip().lower() for word in new_words)
        with open("data/ignore_words.json", "w", encoding="utf-8") as file:
            json.dump(list(ignore_words), file, ensure_ascii=False, indent=4)
