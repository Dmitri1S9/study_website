import math
from collections import Counter
from typing import Dict, List

# from app.services.data_processor.dataInitialization import DataInit
from services.data_processor.dataInitialization import DataInit


# ======== numeric helpers ========

def _log1p(x):
    """Apply log1p to all values, clipping negatives to 0."""
    return [math.log1p(max(v, 0.0)) for v in x]


def _soft_threshold(vals, tau_ratio=0.35):
    """
    Soft threshold: subtract tau from all values, floor at 0.
    tau is a fraction of the max value.
    """
    if not vals:
        return vals
    m = max(vals)
    tau = tau_ratio * m if m > 0 else 0.0
    return [max(v - tau, 0.0) for v in vals]


def _softmax(vals, T=0.8):
    """
    Temperature softmax, numerically stabilized.
    """
    if not vals:
        return vals
    if T <= 0:
        T = 1e-6
    zmax = max(vals) / T
    exps = [math.exp(v / T - zmax) for v in vals]
    s = sum(exps)
    return [e / s if s > 0 else 0.0 for e in exps]


def _largest_remainder_percent(prob, keys, total=100):
    """
    Convert probabilities to integer percentages that sum to `total`
    using the largest remainder method.
    """
    if not prob:
        return {}
    s = sum(prob)
    if s <= 0:
        return {k: 0 for k in keys}
    raw = [p / s * total for p in prob]
    floors = [int(math.floor(x)) for x in raw]
    rem = total - sum(floors)
    frac_idx = sorted(
        range(len(raw)),
        key=lambda i: (raw[i] - floors[i]),
        reverse=True
    )
    for i in range(rem):
        floors[frac_idx[i]] += 1
    return {keys[i]: floors[i] for i in range(len(keys))}


def _soft_tail_mix(prob, keys, top_k=3, tail_shrink=0.35):
    """
    Keep top_k categories as is, shrink the tail by tail_shrink factor,
    then renormalize.
    """
    if not prob:
        return {k: 0.0 for k in keys}
    k = min(top_k, len(prob))
    idx_top = set(sorted(range(len(prob)), key=lambda i: prob[i], reverse=True)[:k])
    mixed = [prob[i] if i in idx_top else prob[i] * tail_shrink
             for i in range(len(prob))]
    s = sum(mixed)
    return [v / s if s > 0 else 0.0 for v in mixed]


# ======== clothing / politics / professions normalization ========

def normalize_clothing(raw_bucket: dict,
                       top_k: int = 3,
                       T: float = 0.8,
                       tau_ratio: float = 0.35,
                       tail_shrink: float = 0.35,
                       min_total: int = 3) -> dict:
    """
    Normalize clothing buckets to 0–100 with smoothing and tail shrinking.
    Small total counts are treated as 'no signal' and return zeros.
    """
    if not raw_bucket:
        return {}
    keys = list(raw_bucket.keys())
    total_raw = sum(float(raw_bucket[k]) for k in keys)
    if total_raw < min_total:
        return {k: 0 for k in keys}

    vals = [float(raw_bucket[k]) for k in keys]
    vals = _log1p(vals)
    vals = _soft_threshold(vals, tau_ratio=tau_ratio)
    if sum(vals) <= 0:
        return {k: 0 for k in keys}

    p = _softmax(vals, T=T)
    p_mix = _soft_tail_mix(p, keys, top_k=top_k, tail_shrink=tail_shrink)
    p_list = list(p_mix)
    return _largest_remainder_percent(p_list, keys, total=100)


def _normalize_politics_axis(raw_bucket: dict,
                             prefix: str,
                             T: float,
                             tau_ratio: float,
                             extreme_weight: float,
                             min_total: int):
    """
    Normalize one politics axis (econ_ or auth_) into 5 buckets + scalar index.
    Index is 0–100 where 50 is middle point.
      econ_axis: 0 = far_left, 100 = far_right
      auth_axis: 0 = strict/order, 100 = anarchy
    """
    if prefix == "econ":
        keys = [
            "econ_far_left_1",
            "econ_soft_left_2",
            "econ_center_3",
            "econ_soft_right_4",
            "econ_far_right_5",
        ]
    else:  # "auth"
        keys = [
            "auth_strict_1",
            "auth_order_2",
            "auth_center_3",
            "auth_freedom_4",
            "auth_anarchy_5",
        ]

    raw_vals = [float(raw_bucket.get(k, 0.0)) for k in keys]
    total_raw = sum(raw_vals)
    if total_raw < min_total:
        # no reliable signal → all zero buckets, neutral axis
        return {k: 0 for k in keys}, 50

    # extra weight for extremes
    if raw_vals:
        raw_vals[0] *= extreme_weight
        raw_vals[-1] *= extreme_weight

    vals = _log1p(raw_vals)
    vals = _soft_threshold(vals, tau_ratio=tau_ratio)
    if sum(vals) <= 0:
        return {k: 0 for k in keys}, 50

    p = _softmax(vals, T=T)
    bucket_percent = _largest_remainder_percent(p, keys, total=100)

    # positions along axis: 0..1 with 0.5 center
    positions = [0.0, 0.25, 0.5, 0.75, 1.0]
    axis_raw = sum(p[i] * positions[i] for i in range(len(positions)))
    axis_index = int(round(axis_raw * 100.0))
    axis_index = max(0, min(100, axis_index))

    return bucket_percent, axis_index


def normalize_politics(raw_bucket: dict,
                       T: float = 0.9,
                       tau_ratio: float = 0.35,
                       extreme_weight: float = 3.0,
                       min_total: int = 3) -> dict:
    """
    Normalize politics buckets into percentages for econ/auth axes.
    Additionally compute scalar axes:
      econ_axis: 0 (far_left) .. 100 (far_right), 50 = center
      auth_axis: 0 (strict)   .. 100 (anarchy),   50 = center
    """
    if not raw_bucket:
        return {}

    out = {}

    econ_buckets, econ_axis = _normalize_politics_axis(
        raw_bucket, prefix="econ",
        T=T, tau_ratio=tau_ratio,
        extreme_weight=extreme_weight,
        min_total=min_total
    )
    auth_buckets, auth_axis = _normalize_politics_axis(
        raw_bucket, prefix="auth",
        T=T, tau_ratio=tau_ratio,
        extreme_weight=extreme_weight,
        min_total=min_total
    )

    out.update(econ_buckets)
    out.update(auth_buckets)
    out["econ_axis"] = econ_axis
    out["auth_axis"] = auth_axis

    # мы возвращаем только оси, сами корзины не нужны
    keys = [
        "econ_far_left_1",
        "econ_soft_left_2",
        "econ_center_3",
        "econ_soft_right_4",
        "econ_far_right_5",
        "auth_strict_1",
        "auth_order_2",
        "auth_center_3",
        "auth_freedom_4",
        "auth_anarchy_5",
    ]
    for key in keys:
        if key in out:
            del out[key]

    return out


def normalize_professions(raw_bucket: dict,
                          top_k: int = 6,
                          T: float = 0.9,
                          tau_ratio: float = 0.35,
                          tail_shrink: float = 0.4,
                          total: int = 100,
                          min_total: int = 3) -> dict:
    """
    Normalize profession buckets to `total` with smoothing and tail shrink.
    Very small totals are treated as 'no signal' and return zeros.
    """
    if not raw_bucket:
        return {}
    keys = list(raw_bucket.keys())
    total_raw = sum(float(raw_bucket[k]) for k in keys)
    if total_raw < min_total:
        return {k: 0 for k in keys}

    vals = [float(raw_bucket[k]) for k in keys]
    vals = _log1p(vals)
    vals = _soft_threshold(vals, tau_ratio=tau_ratio)
    if sum(vals) <= 0:
        return {k: 0 for k in keys}

    p = _softmax(vals, T=T)
    p_mix = _soft_tail_mix(p, keys, top_k=top_k, tail_shrink=tail_shrink)
    p_list = list(p_mix)
    return _largest_remainder_percent(p_list, keys, total=total)


# ======== main collector ========

class DataCollector(DataInit):
    def __init__(self, character_name: str) -> None:
        super().__init__(character_name)

    @staticmethod
    def _get_all_most_relevant_attributes(most_relevant_attributes: Dict,
                                          min_significance: float = 0.15) -> Dict:
        res = {}  # return dict
        for thema in most_relevant_attributes:
            res[thema] = DataCollector._get_one_most_relevant_attributes(
                most_relevant_attributes[thema],
                min_significance
            )
        return res

    @staticmethod
    def _get_one_most_relevant_attributes(most_relevant_attributes: Dict,
                                          min_significance: float = 0.15) -> Dict:
        if not most_relevant_attributes:
            return {}
        all_attributes_summa = max(most_relevant_attributes.values())
        min_significance_level = math.ceil(all_attributes_summa * min_significance)
        return {
            k: max(v, 0) if v >= min_significance_level else 0
            for k, v in most_relevant_attributes.items()
        }

    @staticmethod
    def average_find(l: List) -> int:
        if not l or len(l) != 2:
            raise ValueError
        pos_raw, neg_raw = l
        if pos_raw < 0:
            neg_raw += pos_raw
            pos_raw = 0
        if neg_raw > 0:
            pos_raw += neg_raw
            neg_raw = 0

        pos = max(pos_raw, 0.0)
        neg = abs(min(neg_raw, 0.0))

        delta = max(neg_raw, pos_raw) * 0.05
        enorm = lambda a: max(a - delta, 0)
        pos = enorm(pos)
        neg = enorm(neg)

        ratio = (pos - neg) / (pos + neg + 1)
        return round(ratio * 50 + 50)

    def collect_with_traits(self, d_k: str) -> None:
        pos, neg = 0, 0
        pos_words = self.result_stats[d_k]["positive_traits"]
        neg_words = self.result_stats[d_k]["negative_traits"]

        for word in pos_words:
            cnt = self.words_counter.get(word, 0)
            if cnt > 0:
                pos += cnt

        for word in neg_words:
            cnt = self.words_counter.get(word, 0)
            if cnt > 0:
                neg -= cnt

        self.results[d_k] = [pos, neg]

    def collect_with_attr(self, d_k: str) -> None:
        most_relevant_attributes = dict(
            zip(self.result_stats[d_k], [0] * len(self.result_stats[d_k]))
        )
        for thema in self.result_stats[d_k]:
            for word in self.result_stats[d_k][thema]:
                if word in self.words_counter:
                    most_relevant_attributes[thema] += self.words_counter[word]
            if most_relevant_attributes[thema] <= 0:
                most_relevant_attributes[thema] = 0

        self.results[d_k] = self._get_one_most_relevant_attributes(
            most_relevant_attributes,
            0.10
        )

    def character_compare(self, typ: str) -> None:
        base_key = "character"
        k = 1.0 if typ == "character" else 0.3

        if typ == "character":
            # инициализируем оси
            self.results[base_key] = {
                thema: [0, 0]
                for thema in self.result_stats["character"]["positive_traits"]
            }

        stats = self.result_stats[typ]

        for thema in self.result_stats["character"]["positive_traits"]:
            pos_words = stats["positive_traits"].get(thema, [])
            neg_words = stats["negative_traits"].get(thema, [])

            for word in pos_words:
                cnt = self.words_counter.get(word, 0)
                if cnt > 0:
                    self.results[base_key][thema][0] += int(cnt * k)

            for word in neg_words:
                cnt = self.words_counter.get(word, 0)
                if cnt > 0:
                    self.results[base_key][thema][1] -= int(cnt * k)

    def collect_data(self) -> None:
        print(self.words_counter)
        self.collect_with_traits("attitude")
        self.collect_with_traits("appearance")
        self.collect_with_attr("clothing")
        self.collect_with_attr("politics")
        self.collect_with_attr("professions")
        self.character_compare("character")
        self.character_compare("character_low")
        # print(self.results["character"])

    def normalize(self) -> None:
        """
        Нормализуем все характеристики в удобный вид.
        """
        self.results["attitude"] = self.average_find(self.results["attitude"])
        self.results["appearance"] = self.average_find(self.results["appearance"])

        self.results["character"] = {
            thema: f"{self.average_find(self.results['character'][thema])}%"
            for thema in self.results["character"]
        }

        self.results["clothing"] = normalize_clothing(self.results["clothing"])
        self.results["politics"] = normalize_politics(self.results["politics"])
        self.results["professions"] = normalize_professions(self.results["professions"])
