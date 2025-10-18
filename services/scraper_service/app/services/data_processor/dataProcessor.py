import json
import math
from typing import List, Dict, Any
from wordAnalyser import get_related_words
from scraper_service.app.services.data_processor.dataInitialization import DataCollector
from scraper_service.app.services.db import Database

class DataProcessor(DataCollector):
    def __init__(self, database: Database) -> None:
        super().__init__(database)

    def __str__(self):
        if not self._results: return "No results available."
        my_sep = "-" * 40; res = ""
        for key in self._results: res += f"{key}: {self._results[key]}" + f"\n{my_sep}\n\n"
        return res

    def _count_words(self, text: List[str], score: int) -> None:
        for word in text:
            if word in self._words:
                self._words_counter[word] += round(math.log(score))
            elif self._word_in_characters(word):
                related_words = get_related_words(word)
                for i in related_words:
                    if i in self._words and i not in self._ignore_words:
                        self._words_counter[i] += round(math.log(score) * 0.5)
                        self._words.add(i)
            else:
                self._ignore_words.add(word)

    def _process_text(self):
        database = self.db.character_data
        for user_name, user_posts in database.items():
            for post in user_posts:
                self._count_words(
                    text=self.textProcessor.clean_text(post["title"], self._ignore_words),
                    score=post["score"]
                )
                for comment in post["comments"]:
                    self._count_words(
                        text=self.textProcessor.clean_text(comment["text"], self._ignore_words),
                        score=comment["score"]
                    )

    def _word_in_characters(self, word: str) -> bool:
        if self._get_path.get(word) is None:
            return False
        for path in self._get_path[word]:
            if "character" in path:
                return True
        else:
            return False


