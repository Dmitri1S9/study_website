import math
from collections import Counter
from typing import Dict

from dataProcessor import DataProcessor
from scraper_service.app.services.db import Database

class DataCollector(DataProcessor):
    @staticmethod
    def _get_all_most_relevant_attributes(most_relevant_attributes: Dict, min_significance: float = 0.7) -> Dict:
        res = {}  # return dict
        for thema in most_relevant_attributes:
            res[thema] = DataCollector._get_one_most_relevant_attributes(most_relevant_attributes[thema],
                                                                         min_significance)
        return res

    @staticmethod
    def _get_one_most_relevant_attributes(most_relevant_attributes: Dict, min_significance: float = 0.7) -> Dict:
        if not most_relevant_attributes:
            return {}
        all_attributes_summa = max(most_relevant_attributes.values())
        min_significance_level = math.ceil(all_attributes_summa * min_significance)
        return {k: v for k, v in most_relevant_attributes.items() if v >= min_significance_level}

    def __init__(self, database: Database):
        super().__init__(database)

    def _collect_data(self):
        # Attitude
        self._results["attitude"] = [0, 0]  # positive, negative
        for word in self._result_stats["attitude"]["positive_traits"]:
            if word in self._words_counter:
                self._results["attitude"][0] += self._words_counter[word]
        for word in self._result_stats["attitude"]["negative_traits"]:
            if word in self._words_counter:
                self._results["attitude"][1] -= self._words_counter[word]

        # Appearance
        most_relevant_attributes: Dict[str, Counter[str]] = {}
        for thema in self._result_stats["appearance"]:
            most_relevant_attributes[thema] = Counter()
            for word in self._result_stats["appearance"][thema]:
                if word in self._words_counter:
                    count = self._words_counter[word]
                    if count > 3:
                        most_relevant_attributes[thema].update({word: count})
        self._results["appearance"] = self._get_all_most_relevant_attributes(most_relevant_attributes)

        # Character
        self._results["character"]: Dict = {thema: [0, 0] for thema in
                                            self._result_stats["character"]["positive_traits"]}
        for thema in self._result_stats["character"]["positive_traits"]:
            for word in self._result_stats["character"]["positive_traits"][thema]:
                if word in self._words_counter:
                    self._results["character"][thema][0] += self._words_counter[word]
            for word in self._result_stats["character"]["negative_traits"][thema]:
                if word in self._words_counter:
                    self._results["character"][thema][1] -= self._words_counter[word]

        # Politics
        most_relevant_attributes = dict(zip(self._result_stats["politics"], [0] * len(self._result_stats["politics"])))
        for thema in self._result_stats["politics"]:
            for word in self._result_stats["politics"][thema]:
                if word in self._words_counter:
                    most_relevant_attributes[thema] += self._words_counter[word]
        self._results["politics"] = self._get_one_most_relevant_attributes(most_relevant_attributes, 0.9)

        # Professions
        most_relevant_attributes : Dict = {}
        for profession in self._result_stats["professions"]:
            if profession in self._words_counter:
                most_relevant_attributes[profession] = self._words_counter[profession]
        self._results["professions"] = self._get_one_most_relevant_attributes(most_relevant_attributes)
