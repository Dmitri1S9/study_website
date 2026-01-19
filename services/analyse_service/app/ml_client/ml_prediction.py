import os
from random import randint
from typing import Tuple
import numpy as np
from oci.golden_gate.models import GoogleBigQueryConnection

from app.db import DBGet
from app.ml_client.ml_config import MODEL_DIR
from app.ml_client.ml_entities import Character
from app.ml_client.ml_file_control import load_model


def shrink_to_base(p: float, base: float, alpha: float = 0.01) -> float:
    return float((1 - alpha) * p + alpha * base)


class MLPrediction:
    @staticmethod
    def predict_from_profile(character_: Character, feature_name: str, group: str) -> Tuple[float, float, float]:
        payload = load_model(os.path.join(MODEL_DIR, group, f"model_{feature_name}.joblib"))

        model = payload["model"]
        order = payload["order"]
        oob_mae = payload["oob_mae"]
        base_rate = float(payload.get("base_rate", 0.0))
        target_idx = int(payload["feature_pos"])
        fill_value = float(payload["fill_value"])

        original = float(character_.flat().get(feature_name, 0.0) or 0.0)
        x = character_.to_vector(order)
        x[target_idx] = fill_value
        predicted = shrink_to_base(float(model.predict(x.reshape(1, -1))[0]), base_rate, alpha=0.01)

        return original, predicted, base_rate, oob_mae


if __name__ == "__main__":
    from prettytable import PrettyTable

    db_get = DBGet()
    feature = "flag_serious_violent_crime"

    table = PrettyTable()
    table.field_names = ["name", "universe", "orig", "base", "all", "app", "prof", "psy", "stat", "delta_all", "spread"]

    cl = db_get.get_all_characters()

    for i in range(10):
        ch = cl[(34 * randint(123, 2345) + i * 324) % len(cl)]
        character = Character(profile=ch, character_id=i)

        base = MLPrediction.predict_from_profile(character, feature, "all")[2]

        orig = float(character.flat().get(feature, 0.0) or 0.0)

        oob_mae_all = MLPrediction.predict_from_profile(character, feature, "all")[3]
        oob_mae_2 = MLPrediction.predict_from_profile(character, feature, "psycho")[3]

        all_v = MLPrediction.predict_from_profile(character, feature, "all")[1]
        app_v = MLPrediction.predict_from_profile(character, feature, "appearance")[1]
        prof_v = MLPrediction.predict_from_profile(character, feature, "profession")[1]
        psy_v = MLPrediction.predict_from_profile(character, feature, "psycho")[1]
        stat_v = MLPrediction.predict_from_profile(character, feature, "stat")[1]

        delta_all = all_v - base
        spread = max(all_v, app_v, prof_v, psy_v, stat_v) - min(all_v, app_v, prof_v, psy_v, stat_v)

        table.add_row([
            character.name, character.universe,
            round(orig, 3), round(base, 3),
            round(all_v, 3), round(app_v, 3), round(prof_v, 3), round(psy_v, 3), round(stat_v, 3),
            round(delta_all, 3), round(spread, 3),
        ])

    print(table)
    print("oob_mae: ", oob_mae_all, oob_mae_2)
