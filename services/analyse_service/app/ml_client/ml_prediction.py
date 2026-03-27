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

    for i in range(1):
        # ch = cl[(34 * randint(123, 2345) + i * 324) % len(cl)]

        ch = {
"name": "Dmitrii",
"universe": "Real life",
"age_physical": 1,
"age_mental": 1,
"appearance_cute": 41,
"appearance_charismatic": 41,
"appearance_cool": 31,
"appearance_scary": 31,
"appearance_elegant": 31,
"appearance_sexual": 31,
"appearance_neat": 41,
"appearance_aura": 31,
"behavior_secretive": 60,
"behavior_playful": 50,
"behavior_aggressive": 60,
"behavior_calm": 40,
"behavior_dominant": 50,
"behavior_submissive": 40,
"personality_extraversion": 21,
"character_honesty": 51,
"character_empathy": 21,
"character_loyalty": 61,
"character_justice": 40,
"character_self_control": 31,
"character_ambition": 61,
"character_optimism": 21,
"character_cynicism": 91,
"character_manipulativeness": 40,
"character_risk_taking": 50,
"character_emotional_stability": 40,
"character_humor": 71,
"character_sarcasm": 81,
"character_romantic_intensity": 50,
"character_violence_for_goal": 30,
"character_psych_violence_for_goal": 30,
"character_ideology_focus": 50,
"character_self_sacrifice": 40,
"character_work_focus": 61,
"character_knowledge_drive": 91,
"character_rowdiness": 30,
"character_norm_compliance": 40,
"sin_pride": 60,
"sin_envy": 40,
"sin_wrath": 60,
"sin_greed": 40,
"sin_lust": 40,
"sin_sloth": 81,
"sin_gluttony": 50,
"profession_academic": 81,
"profession_technical": 81,
"profession_military": 1,
"profession_political": 1,
"profession_business": 1,
"profession_criminal": 1,
"profession_religious": 1,
"profession_adventurer": 1,
"politics_econ_axis": 101,
"politics_auth_axis": 21,
"motivation_power": 40,
"motivation_love": 40,
"motivation_duty": 50,
"motivation_freedom": 91,
"motivation_justice": 40,
"motivation_survival": 60,
"motivation_knowledge": 91,
"motivation_greed": 71,
"stat_phys_strength": 51,
"stat_intellect": 81,
"stat_mystic_power": 1,
"stat_influence": 40,
"stat_wealth": 21,
"stat_social_status": 40,
"flag_overweight": 0,
"flag_plays_victim": 0,
"flag_karen_rude": 0,
"flag_2d_character": 0,
"flag_war_criminal": 0,
"flag_killer": 0,
"flag_serious_violent_crime": 0,
"flag_thief": 0,
"flag_organized_crime": 0,
"flag_has_pet": 0,
"flag_laconic": 0,
"flag_slender": 0,
"flag_crazy": 0,
"flag_pacifist": 0,
"flag_moralist": 0,
"flag_woke": 0,
"flag_knight": 0,
"flag_leader": 0
}
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