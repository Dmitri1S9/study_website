import os
from typing import Any, Dict, List, Tuple
from prettytable import PrettyTable

from app.db import DBGet
from app.ml_client.ml_config import MODEL_DIR
from app.ml_client.ml_entities import Character
from app.ml_client.ml_file_control import load_model


FEATURE = "flag_serious_violent_crime"
MODEL_ALL = "all"
MODEL_PSY = "psycho"

# Порог для "pred" (если хочешь показывать не только score, но и 0/1 решение)
THR = 0.40


# -------------- utils --------------
def shrink_to_base(p: float, base: float, alpha: float = 0.01) -> float:
    return float((1 - alpha) * p + alpha * base)


def to_label(v: Any) -> int:
    try:
        return 1 if float(v or 0.0) >= 0.5 else 0
    except (TypeError, ValueError):
        return 0


# -------------- prediction wrapper --------------
class MLPrediction:
    @staticmethod
    def predict_from_profile(character_: Character, feature_name: str, group: str) -> Tuple[float, float, float, float]:
        path = os.path.join(str(MODEL_DIR), group, f"model_{feature_name}.joblib")
        payload = load_model(path)

        model = payload["model"]
        order = payload["order"]
        oob_mae = float(payload["oob_mae"])
        base_rate = float(payload.get("base_rate", 0.0))
        target_idx = int(payload["feature_pos"])
        fill_value = float(payload["fill_value"])

        original = float(character_.flat().get(feature_name, 0.0) or 0.0)

        x = character_.to_vector(order)
        x[target_idx] = fill_value

        predicted = float(model.predict(x.reshape(1, -1))[0])
        predicted = shrink_to_base(predicted, base_rate, alpha=0.01)

        return original, predicted, base_rate, oob_mae


# -------------- main --------------
if __name__ == "__main__":
    db_get = DBGet()

    # Лучше хранить кандидатов как (name, universe), чтобы не ловить коллизии типа "L"
    CANDIDATES: List[Tuple[str, str]] = [
        ("Light Yagami", "Death Note"),
        ("L", "Death Note"),
        ("Ryuk", "Death Note"),
        ("Misa Amane", "Death Note"),

        ("Guts", "Berserk"),
        ("Griffith", "Berserk"),
        ("Casca", "Berserk"),

        ("Edward Elric", "Fullmetal Alchemist"),
        ("Alphonse Elric", "Fullmetal Alchemist"),
        ("Roy Mustang", "Fullmetal Alchemist"),

        ("Shinji Ikari", "Neon Genesis Evangelion"),
        ("Rei Ayanami", "Neon Genesis Evangelion"),
        ("Asuka Langley Soryu", "Neon Genesis Evangelion"),

        ("Okabe Rintarou", "Steins;Gate"),
        ("Kurisu Makise", "Steins;Gate"),

        ("Hisoka Morow", "Hunter x Hunter"),

        ("Walter White", "Breaking Bad"),
        ("Jesse Pinkman", "Breaking Bad"),
        ("Gustavo Fring", "Breaking Bad"),

        ("Saul Goodman", "Better Call Saul"),
        ("Lalo Salamanca", "Better Call Saul"),

        ("Tony Soprano", "The Sopranos"),
        ("Hannibal Lecter", "The Silence of the Lambs"),
        ("Clarice Starling", "The Silence of the Lambs"),

        ("Patrick Bateman", "American Psycho"),
        ("Anton Chigurh", "No Country for Old Men"),
        ("John Wick", "John Wick"),
        ("Michael Corleone", "The Godfather"),
    ]

    cand_set = set(CANDIDATES)

    all_profiles = db_get.get_all_characters()
    profiles = [p for p in all_profiles if (p.get("name"), p.get("universe")) in cand_set]

    found_set = {(p.get("name"), p.get("universe")) for p in profiles}
    missing = [c for c in CANDIDATES if c not in found_set]
    if missing:
        print("\nMissing in DB (ignored):")
        for n, u in missing:
            print(f"- {n} | {u}")

    if not profiles:
        print("No candidates found in DB. (universe strings mismatch?)")
        raise SystemExit(0)

    rows: List[Dict[str, Any]] = []

    for i, pr in enumerate(profiles):
        c = Character(profile=pr, character_id=i)

        # orig (0/1 из профиля)
        orig = to_label(c.flat().get(FEATURE, 0.0))

        # scores
        _, all_v, _, _ = MLPrediction.predict_from_profile(c, FEATURE, MODEL_ALL)
        _, psy_v, _, _ = MLPrediction.predict_from_profile(c, FEATURE, MODEL_PSY)

        all_v = float(all_v)
        psy_v = float(psy_v)

        rows.append({
            "name": c.name,
            "universe": c.universe,
            "orig": orig,
            "all": all_v,
            "psy": psy_v,
            "pred_all": 1 if all_v >= THR else 0,
            "pred_psy": 1 if psy_v >= THR else 0,
            "spread": abs(all_v - psy_v),
        })

    # -------- 1) Таблица: порядок по ALL --------
    by_all = sorted(rows, key=lambda r: r["all"], reverse=True)
    t1 = PrettyTable()
    t1.field_names = ["rank_all", "orig", "pred_all", "name", "universe", "all", "psy", "spread"]
    for rank, r in enumerate(by_all, 1):
        t1.add_row([
            rank,
            r["orig"],
            r["pred_all"],
            r["name"],
            r["universe"],
            round(r["all"], 3),
            round(r["psy"], 3),
            round(r["spread"], 3),
        ])

    print("\n=== RANKING BY ALL (all params) ===")
    print(t1)

    # -------- 2) Таблица: порядок по PSY --------
    by_psy = sorted(rows, key=lambda r: r["psy"], reverse=True)
    t2 = PrettyTable()
    t2.field_names = ["rank_psy", "orig", "pred_psy", "name", "universe", "psy", "all", "spread"]
    for rank, r in enumerate(by_psy, 1):
        t2.add_row([
            rank,
            r["orig"],
            r["pred_psy"],
            r["name"],
            r["universe"],
            round(r["psy"], 3),
            round(r["all"], 3),
            round(r["spread"], 3),
        ])

    print("\n=== RANKING BY PSY (psy only) ===")
    print(t2)

    # -------- 3) Два списка (как ты просил) --------
    # Чтобы прямо показывать "как был 0/1" + порядок:
    ALL_ORDER = [[r["orig"], r["name"], r["universe"], round(r["all"], 3), round(r["psy"], 3)] for r in by_all]
    PSY_ORDER = [[r["orig"], r["name"], r["universe"], round(r["psy"], 3), round(r["all"], 3)] for r in by_psy]

    print("\nALL_ORDER =")
    print(ALL_ORDER)

    print("\nPSY_ORDER =")
    print(PSY_ORDER)
