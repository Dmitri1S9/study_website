import math
from collections import Counter
from typing import Dict, List

from services.data_processor.dataInitialization import DataInit


class DataCollector(DataInit):
    @staticmethod
    def _get_all_most_relevant_attributes(most_relevant_attributes: Dict, min_significance: float = 0.15) -> Dict:
        res = {}  # return dict
        for thema in most_relevant_attributes:
            res[thema] = DataCollector._get_one_most_relevant_attributes(most_relevant_attributes[thema],
                                                                         min_significance)
        return res

    @staticmethod
    def _get_one_most_relevant_attributes(most_relevant_attributes: Dict, min_significance: float = 0.15) -> Dict:
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

    def collect_with_traits(self, d_k: str):
        self.results[d_k] = [0, 0]  # positive, negative
        for word in self.result_stats[d_k]["positive_traits"]:
            if word in self.words_counter:
                self.results[d_k][0] += self.words_counter[word]
        for word in self.result_stats[d_k]["negative_traits"]:
            if word in self.words_counter:
                self.results[d_k][1] -= self.words_counter[word]

    def collect_with_attr(self, d_k: str):
        most_relevant_attributes = dict(zip(self.result_stats[d_k], [0] * len(self.result_stats[d_k])))
        for thema in self.result_stats[d_k]:
            for word in self.result_stats[d_k][thema]:
                if word in self.words_counter:
                    most_relevant_attributes[thema] += self.words_counter[word]
                else:
                    most_relevant_attributes[thema] += 0
        self.results[d_k] = self._get_one_most_relevant_attributes(most_relevant_attributes, 0.10)


    def collect_data(self):
        self.collect_with_traits("attitude")
        self.collect_with_traits("appearance")
        self.collect_with_attr("clothing")
        self.collect_with_attr("politics")
        self.collect_with_attr("professions")
        self.results["character"]: Dict = {thema: [0, 0] for thema in
                                            self.result_stats["character"]["positive_traits"]}
        for thema in self.result_stats["character"]["positive_traits"]:
            for word in self.result_stats["character"]["positive_traits"][thema]:
                if word in self.words_counter:
                    self.results["character"][thema][0] += self.words_counter[word]
            for word in self.result_stats["character"]["negative_traits"][thema]:
                if word in self.words_counter:
                    self.results["character"][thema][1] -= self.words_counter[word]


    def normalize(self) -> None:
        """
        normalize characteristics
        """
        self.results["attitude"] = self.average_find(self.results["attitude"], 0.8)
        self.results["appearance"] = self.average_find(self.results["appearance"], 0.8)
        self.results["character"] = {i : str(self.average_find(self.results["character"][i])) + "%" for i in self.results["character"]}

