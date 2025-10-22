import math
from collections import Counter
from typing import Dict, List

from scraper_service.app.services.data_processor.dataInitialization import DataInit


class DataCollector(DataInit):
    @staticmethod
    def _get_all_most_relevant_attributes(most_relevant_attributes: Dict, min_significance: float = 0.3) -> Dict:
        res = {}  # return dict
        for thema in most_relevant_attributes:
            res[thema] = DataCollector._get_one_most_relevant_attributes(most_relevant_attributes[thema],
                                                                         min_significance)
        return res

    @staticmethod
    def _get_one_most_relevant_attributes(most_relevant_attributes: Dict, min_significance: float = 0.3) -> Dict:
        if not most_relevant_attributes:
            return {}
        all_attributes_summa = max(most_relevant_attributes.values())
        min_significance_level = math.ceil(all_attributes_summa * min_significance)
        return {k: max(v, 0) if v >= min_significance_level else 0 for k, v in most_relevant_attributes.items()}


    @staticmethod
    def average_find(l: List, k: float = 0.95) -> int:
        a, b = l
        a *= k  # cause there are more positive comments
        max_v = abs(a) + abs(b) + 1
        return round((a / max_v) * 100)

    def __init__(self, character_name: str) -> None:
        super().__init__(character_name)

    def collect_data(self):
        # Attitude
        self.results["attitude"] = [0, 0]  # positive, negative
        for word in self.result_stats["attitude"]["positive_traits"]:
            if word in self.words_counter:
                self.results["attitude"][0] += self.words_counter[word]
        for word in self.result_stats["attitude"]["negative_traits"]:
            if word in self.words_counter:
                self.results["attitude"][1] -= self.words_counter[word]

        # Appearance
        most_relevant_attributes: Dict[str, Counter[str]] = {}
        for thema in self.result_stats["appearance"]:
            most_relevant_attributes[thema] = Counter()
            for word in self.result_stats["appearance"][thema]:
                if word in self.words_counter:
                    count = self.words_counter[word]
                    if count > 2:
                        most_relevant_attributes[thema].update({word: count})
                    else:
                        most_relevant_attributes[thema].update({word: 0})
                else:
                    most_relevant_attributes[thema].update({word: 0})

        self.results["appearance"] = self._get_all_most_relevant_attributes(most_relevant_attributes)

        # Character
        self.results["character"]: Dict = {thema: [0, 0] for thema in
                                            self.result_stats["character"]["positive_traits"]}
        for thema in self.result_stats["character"]["positive_traits"]:
            for word in self.result_stats["character"]["positive_traits"][thema]:
                if word in self.words_counter:
                    self.results["character"][thema][0] += self.words_counter[word]
            for word in self.result_stats["character"]["negative_traits"][thema]:
                if word in self.words_counter:
                    self.results["character"][thema][1] -= self.words_counter[word]

        # Politics
        most_relevant_attributes = dict(zip(self.result_stats["politics"], [0] * len(self.result_stats["politics"])))
        for thema in self.result_stats["politics"]:
            for word in self.result_stats["politics"][thema]:
                if word in self.words_counter:
                    most_relevant_attributes[thema] += self.words_counter[word]
                else:
                    most_relevant_attributes[thema] += 0
        self.results["politics"] = self._get_one_most_relevant_attributes(most_relevant_attributes, 0.9)

        # Professions
        most_relevant_attributes : Dict = {}
        for profession in self.result_stats["professions"]:
            if profession in self.words_counter:
                most_relevant_attributes[profession] = self.words_counter[profession]
            else:
                most_relevant_attributes[profession] = 0
        self.results["professions"] = self._get_one_most_relevant_attributes(most_relevant_attributes)

    def normalize(self) -> None:
        """
        normalize characteristics
        """
        self.results["attitude"] = self.average_find(self.results["attitude"], 0.8),
        self.results["character"] = {i : str(self.average_find(self.results["character"][i])) + "%" for i in self.results["character"]}

