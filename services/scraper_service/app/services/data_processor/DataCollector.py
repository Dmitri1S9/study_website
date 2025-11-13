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
        if abs(a) > abs(b) * k:
            a *= k
        elif abs(b) > abs(a) * k:
            b *= k
        else:
            ... # I like femboys))))))))))))))))
        max_v = abs(a) + abs(b) + 1
        return round((a / max_v) * 100)

    def __init__(self, character_name: str) -> None:
        super().__init__(character_name)

    def collect_with_traits(self, d_k: str):
        self.results[d_k] = [0, 0]  # positive, negative
        for word in self.result_stats[d_k]["positive_traits"]:
            if word in self.words_counter:
                if self.words_counter[word] >= 0:
                    self.results[d_k][0] += self.words_counter[word]
                else:
                    self.results[d_k][1] += self.words_counter[word]
        for word in self.result_stats[d_k]["negative_traits"]:
            if word in self.words_counter:
                if self.words_counter[word] >= 0:
                    self.results[d_k][1] -= self.words_counter[word]
                else:
                    self.results[d_k][0] -= self.words_counter[word]

    def collect_with_attr(self, d_k: str):
        most_relevant_attributes = dict(zip(self.result_stats[d_k], [0] * len(self.result_stats[d_k])))
        for thema in self.result_stats[d_k]:
            for word in self.result_stats[d_k][thema]:
                if word in self.words_counter:
                    most_relevant_attributes[thema] += self.words_counter[word]
                else:
                    most_relevant_attributes[thema] += 0
            if most_relevant_attributes[thema] <= 0:
                most_relevant_attributes[thema] = 0
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
        self.results["clothing"] = normalize_clothing(self.results["clothing"])
        self.results["politics"] = normalize_politics(self.results["politics"])
        self.results["professions"] = normalize_professions(self.results["professions"])


def _log1p(x):
    return [math.log1p(max(v, 0.0)) for v in x]

def _soft_threshold(vals, tau_ratio=0.35):
    if not vals:
        return vals
    m = max(vals)
    tau = tau_ratio * m if m > 0 else 0.0
    return [max(v - tau, 0.0) for v in vals]

def _softmax(vals, T=0.8):
    if not vals:
        return vals
    if T <= 0:
        T = 1e-6
    zmax = max(vals) / T
    exps = [math.exp(v / T - zmax) for v in vals]
    s = sum(exps)
    return [e / s if s > 0 else 0.0 for e in exps]

def _largest_remainder_percent(prob, keys, total=100):
    if not prob:
        return {}
    s = sum(prob)
    if s <= 0:
        return {k: 0 for k in keys}
    raw = [p / s * total for p in prob]
    floors = [int(math.floor(x)) for x in raw]
    rem = total - sum(floors)
    frac_idx = sorted(range(len(raw)), key=lambda i: (raw[i] - floors[i]), reverse=True)
    for i in range(rem):
        floors[frac_idx[i]] += 1
    return {keys[i]: floors[i] for i in range(len(keys))}

def _soft_tail_mix(prob, keys, top_k=3, tail_shrink=0.35):
    if not prob:
        return {k: 0.0 for k in keys}
    k = min(top_k, len(prob))
    idx_top = set(sorted(range(len(prob)), key=lambda i: prob[i], reverse=True)[:k])
    mixed = [prob[i] if i in idx_top else prob[i] * tail_shrink for i in range(len(prob))]
    s = sum(mixed)
    mixed = [v / s if s > 0 else 0.0 for v in mixed]
    return {keys[i]: mixed[i] for i in range(len(keys))}

def normalize_clothing(raw_bucket: dict,
                       top_k: int = 3,
                       T: float = 0.8,
                       tau_ratio: float = 0.35,
                       tail_shrink: float = 0.35) -> dict:
    if not raw_bucket:
        return {}
    keys = list(raw_bucket.keys())
    vals = [float(raw_bucket[k]) for k in keys]
    vals = _log1p(vals)
    vals = _soft_threshold(vals, tau_ratio=tau_ratio)
    if sum(vals) <= 0:
        return {k: 0 for k in keys}
    p = _softmax(vals, T=T)
    p_mix = _soft_tail_mix(p, keys, top_k=top_k, tail_shrink=tail_shrink)
    p_list = [p_mix[k] for k in keys]
    return _largest_remainder_percent(p_list, keys, total=100)

def _normalize_pair(a, b, T=0.95, tau_ratio=0.30):
    av, bv = float(a), float(b)
    av = math.log1p(max(av, 0.0))
    bv = math.log1p(max(bv, 0.0))
    m = max(av, bv)
    tau = tau_ratio * m if m > 0 else 0.0
    av = max(av - tau, 0.0)
    bv = max(bv - tau, 0.0)
    s = av + bv
    if s <= 0:
        return 0.5, 0.5
    if T <= 0:
        T = 1e-6
    zmax = max(av, bv) / T
    ea = math.exp(av / T - zmax)
    eb = math.exp(bv / T - zmax)
    denom = ea + eb
    return (ea / denom, eb / denom)

def normalize_politics(raw_bucket: dict, T: float = 0.95, tau_ratio: float = 0.30) -> dict:
    pairs = [
        ("economic_left", "economic_right"),
        ("authoritarian", "libertarian"),
    ]

    out = {}
    for a, b in pairs:
        pa, pb = _normalize_pair(raw_bucket.get(a, 0.0),
                                 raw_bucket.get(b, 0.0),
                                 T=T, tau_ratio=tau_ratio)
        raw = [pa * 100.0, pb * 100.0]
        floors = [int(math.floor(x)) for x in raw]
        rem = 100 - sum(floors)
        frac_idx = sorted(range(2), key=lambda i: raw[i] - floors[i], reverse=True)
        for i in range(rem):
            floors[frac_idx[i % 2]] += 1
        out[a] = floors[0]
        out[b] = floors[1]
    return out

def normalize_professions(raw_bucket: dict,
                          top_k: int = 6,
                          T: float = 0.9,
                          tau_ratio: float = 0.35,
                          tail_shrink: float = 0.4,
                          total: int = 100) -> dict:
    if not raw_bucket:
        return {}
    keys = list(raw_bucket.keys())
    vals = [float(raw_bucket[k]) for k in keys]
    vals = _log1p(vals)
    vals = _soft_threshold(vals, tau_ratio=tau_ratio)
    if sum(vals) <= 0:
        return {k: 0 for k in keys}
    p = _softmax(vals, T=T)
    p_mix = _soft_tail_mix(p, keys, top_k=top_k, tail_shrink=tail_shrink)
    p_list = [p_mix[k] for k in keys]
    return _largest_remainder_percent(p_list, keys, total=total)



