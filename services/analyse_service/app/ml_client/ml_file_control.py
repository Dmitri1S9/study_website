import json
import os
from pathlib import Path
from typing import Dict

from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier

from app.ml_client.ml_config import MEDIANS_PATH, VERSION, MODEL_DIR


def load_model(path: str):
    return load(path)

def save_model(path: str, model_: RandomForestClassifier, feature_pos: int, order_: list[str],
               fill_value: int, seed: int, n_estimators: int, base_rate: float, drop_p, rf_max_depth, rf_min_leaf, oob_mae) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "model": model_,
        "feature_pos": feature_pos,
        "feature_name": order_[feature_pos],
        "order": order_,
        "fill_value": fill_value,
        "seed": seed,
        "base_rate": base_rate,
        "n_estimators": n_estimators,
        "drop_p": drop_p,
        "rf_max_depth": rf_max_depth,
        "rf_min_leaf": rf_min_leaf,
        "oob_mae": oob_mae
    }
    dump(payload, path)

def save_medians_json(medians: Dict[str, float]) -> None:
    with open(MEDIANS_PATH, "w", encoding="utf-8") as f:
        json.dump(medians, f, ensure_ascii=False, indent=2)


def load_medians_json(path: str = MEDIANS_PATH) -> Dict[str, float]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: float(v) for k, v in data.items()}
