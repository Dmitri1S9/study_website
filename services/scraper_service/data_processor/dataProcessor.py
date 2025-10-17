import json
import math
from collections import Counter
from typing import List, Dict, Any
from wordAnalyse import get_related_words
from scraper_service.data_processor.dataHandler import DataHandler
from textClean import TextCleaner

class DataProcessor(DataHandler):
    @staticmethod
    def _get_most_relevant_attributes(most_relevant_attributes, min_significance : int = 0.7) -> Dict:
        res = {} # return dict
        for thema in most_relevant_attributes:
            all_attributes_summa = max(most_relevant_attributes[thema].values())
            min_significance_level = math.ceil(all_attributes_summa * min_significance)
            res[thema] = {
                k: v for k, v in most_relevant_attributes[thema].items()
                          if v >= min_significance_level
            }
        return res

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
        with open("data/db.json", "r", encoding="utf-8") as file:
            database: Dict[str, Any] = json.load(file)
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

    def _collect_dirty_data(self):
        self._results["attitude"] = [0, 0]  # positive, negative
        for word in self._database_new["attitude"]["positive_traits"]:
            if word in self._words_counter:
                self._results["attitude"][0] += self._words_counter[word]
        for word in self._database_new["attitude"]["negative_traits"]:
            if word in self._words_counter:
                self._results["attitude"][1] -= self._words_counter[word]

        most_relevant_attributes : Dict[str: Counter[str]] = {}
        for thema in self._database_new["appearance"]:
            most_relevant_attributes[thema] = Counter()
            for word in self._database_new["appearance"][thema]:
                if word in self._words_counter:
                    count = self._words_counter[word]
                    if count > 3:
                        most_relevant_attributes[thema].update({word: count})
        self._results["appearance"] = self._get_most_relevant_attributes(most_relevant_attributes)

        character_data = {}
        for thema in self._database_new["character"]["positive_traits"]:
            character_data[thema] = 0
        for thema in self._database_new["character"]["positive_traits"]:
            for word in self._database_new["character"]["positive_traits"][thema]:
                if word in self._words_counter:
                    character_data[thema] += self._words_counter[word]
            for word in self._database_new["character"]["negative_traits"][thema]:
                if word in self._words_counter:
                    character_data[thema] -= self._words_counter[word]

        self._results["character"] = character_data

        self._results["politics"] = dict(zip(self._database_new["politics"], [0] * len(self._database_new["politics"])))
        for thema in self._database_new["politics"]:
            for word in self._database_new["politics"][thema]:
                if word in self._words_counter:
                    self._results["politics"][thema] += self._words_counter[word]

        self._results["professions"] = {}
        for profession in self._database_new["professions"]:
            if profession in self._words_counter:
                self._results["professions"][profession] = self._words_counter[profession]
        self._results["professions"] = Counter(self._results["professions"])

    def run(self):
        self._create_result_database()
        self._process_text()
        self._collect_dirty_data()
        print(self)

if __name__ == "__main__":
    with DataProcessor() as processor:
        processor.run()

