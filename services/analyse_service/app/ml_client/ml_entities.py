import logging
import statistics
from typing import Dict, List, Iterator, Tuple, Any, Optional

import numpy as np

from app.ml_client.ml_config import MEDIANS_PATH, AVOID
from app.ml_client.ml_file_control import save_medians_json, load_medians_json

log = logging.getLogger(__name__)



class Character(object):
    def __init__(self, profile: Dict, character_id: int) -> None:
        self.id = character_id
        self._profile = profile
        self.name = profile["name"]
        self.universe = profile["universe"]

        self.stats_0_10 = dict() # [-1, 0-101]
        self.mask = dict()
        self.flags = dict() # [-1, 0, 1]

        self.stats_distribution()

    def __str__(self):
        start_dict = {
            "name": self.name,
            "universe": self.universe
        }
        return str(start_dict | self.flags | self.stats_0_10)

    def __iter__(self):
        return iter(self.flat())

    def flat(self) -> Dict[str, Any]:
        return self.flags | self.stats_0_10

    def ordered_param_names(self):
        return sorted(self.flat().keys())

    def stats_distribution(self) -> None:
        def param_activation(active_param: str, max_value: int) -> None:
            self.stats_0_10[active_param] = (int(self._profile[active_param]) // 10) / max_value \
                if int(self._profile[active_param]) >= 0 else None
            self.mask[active_param] = (int(self._profile[active_param]) % 10
                                if int(self._profile[active_param]) >= 0 else 0)

        for param, value in self._profile.items():
            if param in AVOID:
                continue
            elif param[:4] == "flag":
                self.flags[param] = float(value) if int(value) >= 0 else None
                self.mask[param] = 1 if int(value) >= 0 else 0
            else:
                param_activation(param, 10)
        param_activation("stat_wealth", 4)
        # param_activation("age_mental", 3)
        # param_activation("age_physical", 3)

    def get_stats(self) -> Dict[str, float]:
        return self.flat()

    def get_mask(self):
        return self.mask

    def get_name(self) -> str:
        return self.name

    def get_universe(self) -> int:
        return self.universe

    def to_vector(self, order: List[str]) -> np.ndarray:
        def clear_flat() -> Dict[str, Any]:

            medians = load_medians_json(MEDIANS_PATH)

            flat = self.flat()
            cleared: Dict[str, Any] = {}

            for k, v in flat.items():
                if v is None:
                    if k not in medians:
                        raise KeyError(f"Median not found for key: {k}")
                    cleared[k] = float(medians[k])
                else:
                    cleared[k] = float(v)
            return cleared

        def get_value(key: str) -> float:
            return float(clear_flat()[key])

        return np.array([get_value(k) for k in order], dtype=float)

class CharactersList(object):
    def __init__(self, characters_list: List[Character]) -> None:
        self.characters_list : List[Character] = [
            Character(ch, i) for i, ch in enumerate(characters_list)
        ]
        # declare the order of all lists in matrix
        self.guarantor = self.characters_list[0].ordered_param_names()
        if any(cha.ordered_param_names() != self.guarantor for cha in self.characters_list[1:]):
            raise ValueError("Params of characters are not equal")

        self.dirty_matrix = self.dirty_matrix()
        self.mask = self.mask_matrix()
        self.clear_matrix = self.clear_matrix()

    def get_order(self):
        return self.guarantor

    def dirty_matrix(self) -> Optional[List[List[float | None]]]:
        res = []
        for ch in self.characters_list:
            new_ch : List[float] = []
            for param in self.guarantor:
                new_ch.append(ch.get_stats()[param])
            res.append(new_ch)
        return res

    def median_of_param(self, param_index: int) -> float:
        col = [
            row[param_index]
            for row in self.dirty_matrix
            if row[param_index] is not None
        ]
        if not col:
            return 0.0
        return float(statistics.median(col))

    def clear_matrix(self) -> List[List[float]]:
        if not self.dirty_matrix:
            raise NotImplementedError("no dirty matrix")
        n_cols = len(self.guarantor)
        medians = [self.median_of_param(i) for i in range(n_cols)]

        res: List[List[float]] = []
        for i, row in enumerate(self.dirty_matrix):
            new_row: List[float] = []
            for j, v in enumerate(row):
                if v is None:
                    new_row.append(medians[j])
                else:
                    new_row.append(float(v))
            res.append(new_row)

        return res

    def mask_matrix(self):
        res : List[List[float]] = []
        for ch in self.characters_list:
            new_row : List[float] = []
            for param in self.guarantor:
                new_row.append(ch.get_mask()[param])
            res.append(new_row)
        return res

    def get_medians(self):
        medians = {}
        for idx, name in enumerate(self.guarantor):
            medians[name] = float(self.median_of_param(idx))
        save_medians_json(medians)

    def __str__(self):
        return "\n".join([str(ch) for ch in self.characters_list])

    def __len__(self):
        return len(self.characters_list)

    def __iter__(self):
        return iter(self.characters_list)

    def __getitem__(self, item):
        return self.characters_list[item]


if __name__ == "__main__":
    from app.ml_client.ml_learning import MLLearnContext
    # it's a small cute test
    profiles = MLLearnContext().characters_list
    cl = CharactersList(profiles)

    print(len(cl), "rows")
    print(len(cl.guarantor), "features")
    print("dirty has None:", any(v is None for row in cl.dirty_matrix for v in row))
    print("clear has None:", any(v is None for row in cl.clear_matrix for v in row))
    print("mask range:", min(min(r) for r in cl.mask), max(max(r) for r in cl.mask))







