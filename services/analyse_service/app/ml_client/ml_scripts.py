import numpy as np


def mesh_appearance(param: str):
    return param[:10] == "appearance"

def mesh_behavior(param: str):
    return param[:8] == "behavior"

def mesh_character(param: str):
    return param[:9] == "character" or param[:len("personality")] == "personality"

def mesh_sin(param: str):
    return param[:3] == "sin"

def mesh_profession(param: str):
    return param[:10] == "profession"

def mesh_motivation(param: str):
    return param[:10] == "motivation"

def mesh_stat(param: str):
    return param[:4] == "stat"

def mesh_flag(param: str):
    return param[:4] == "flag"

mesh_psycho = lambda param: (
    mesh_character(param)
    or mesh_behavior(param)
    or mesh_motivation(param)
    or mesh_sin(param)
)
mesh_all = lambda param: (
    mesh_psycho(param)
    or mesh_stat(param)
    or mesh_profession(param)
    or mesh_appearance(param)
    or mesh_flag(param)
)


def slice_by_mesh(target_pos: int, mesh_func, order: dict, matrix : np.ndarray):
    keep_idx = [
        i for i, name in enumerate(order) if mesh_func(name) or i == target_pos
    ]
    order_sliced = [order[i] for i in keep_idx]
    target_idx_in_sliced = order_sliced.index(order[target_pos])

    x_sliced = matrix[:, keep_idx].astype(float).copy()
    return x_sliced, order_sliced, target_idx_in_sliced



import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from prettytable import PrettyTable


# -----------------------------
# CONFIG
# -----------------------------
API_URL = "http://127.0.0.1:8000/get_feature_by_name_and_universe"
FEATURE = "flag_serious_violent_crime"

TIMEOUT = 30
MAX_WORKERS = 10

# Если хочешь "ровно 30" и любые пропуски раздражают:
# просто добавь больше кандидатов в список ниже.
CANDIDATES = [
    # --- Anime / Manga ---
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

    # --- TV / Movies (серые/чёрные/белые) ---
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

# Сколько хотим в исходном наборе (если найдутся)
N_WANTED = 30

# Печатать ли 2 полных списка (по all и по psy) на всём успешном наборе
PRINT_FULL_SORTED = True

# Сколько брать в финальный “максимально разошедшийся” набор
N_FINAL = 10


# -----------------------------
# Helpers
# -----------------------------
def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def fetch_one(name: str, universe: str):
    params = {"name": name, "universe": universe, "feature": FEATURE}
    try:
        r = requests.get(API_URL, params=params, timeout=TIMEOUT)
        js = r.json()
        data = js.get("predicted", {}).get("data", None)

        # твой формат: [orig, all, app, prof, psy, stat]
        orig = data[0] if isinstance(data, list) and len(data) > 0 else None
        all_v = data[1] if isinstance(data, list) and len(data) > 1 else None
        psy_v = data[4] if isinstance(data, list) and len(data) > 4 else None

        orig = safe_float(orig)
        all_v = safe_float(all_v)
        psy_v = safe_float(psy_v)

        ok = (r.status_code == 200 and orig is not None and all_v is not None and psy_v is not None)
        return {
            "name": name,
            "universe": universe,
            "orig": orig,
            "all": all_v,
            "psy": psy_v,
            "http": r.status_code,
            "ok": ok,
        }
    except Exception as e:
        return {
            "name": name,
            "universe": universe,
            "orig": None,
            "all": None,
            "psy": None,
            "http": -1,
            "ok": False,
            "error": str(e),
        }


def rid(r):
    return f"{r['name']} | {r['universe']}"


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # 1) берём первые N_WANTED кандидатов (или меньше)
    wanted = CANDIDATES[:N_WANTED]

    # 2) дергаем API параллельно
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(fetch_one, n, u) for (n, u) in wanted]
        for fut in as_completed(futs):
            results.append(fut.result())

    ok = [r for r in results if r.get("ok")]
    bad = [r for r in results if not r.get("ok")]

    if len(ok) < 10:
        print("Слишком мало успешных ответов API (нужно хотя бы 10).")
        print(f"OK: {len(ok)} / {len(results)}")
        for r in bad[:20]:
            print("fail:", r["universe"], "|", r["name"], "| http=", r.get("http"), "| err=", r.get("error"))
        raise SystemExit(0)

    # 3) сортировки по значению (ALL и PSY)
    sort_all = sorted(ok, key=lambda r: r["all"], reverse=True)
    sort_psy = sorted(ok, key=lambda r: r["psy"], reverse=True)

    # 4) ранги и разница рангов
    rank_all = {rid(r): i for i, r in enumerate(sort_all)}
    rank_psy = {rid(r): i for i, r in enumerate(sort_psy)}
    for r in ok:
        r["rank_all"] = rank_all[rid(r)]
        r["rank_psy"] = rank_psy[rid(r)]
        r["rank_diff"] = abs(r["rank_all"] - r["rank_psy"])

    # 5) выбираем N_FINAL с максимальной разницей рангов
    # tie-break: чем больше max(all, psy) и |all-psy|, тем “вкуснее” для демонстрации
    top = sorted(
        ok,
        key=lambda r: (r["rank_diff"], abs(r["all"] - r["psy"]), max(r["all"], r["psy"])),
        reverse=True
    )[:N_FINAL]

    top_ids = {rid(r) for r in top}
    top_all_order = [r for r in sort_all if rid(r) in top_ids]
    top_psy_order = [r for r in sort_psy if rid(r) in top_ids]

    # ---- Таблица топ-10 по расхождению ----
    t = PrettyTable()
    t.field_names = ["name", "universe", "orig(1)", "all(2)", "psy(5)", "r_all", "r_psy", "diff", "|all-psy|"]
    for r in top:
        t.add_row([
            r["name"], r["universe"],
            round(r["orig"], 3),
            round(r["all"], 3),
            round(r["psy"], 3),
            r["rank_all"],
            r["rank_psy"],
            r["rank_diff"],
            round(abs(r["all"] - r["psy"]), 3),
        ])

    print("\nTOP-10 with MAX rank disagreement (selected from successful API responses)")
    print(t)

    # ---- 2 списка (как ты хотел) ----
    print("\nORDER BY ALL (desc) on TOP-10:")
    for i, r in enumerate(top_all_order, 1):
        print(f"{i:02d}. {r['name']} | {r['universe']}  all={r['all']:.3f}  psy={r['psy']:.3f}  orig={r['orig']:.3f}")

    print("\nORDER BY PSY (desc) on TOP-10:")
    for i, r in enumerate(top_psy_order, 1):
        print(f"{i:02d}. {r['name']} | {r['universe']}  psy={r['psy']:.3f}  all={r['all']:.3f}  orig={r['orig']:.3f}")

    # ---- Если хочешь ещё и два полных списка на всём наборе (до 30) ----
    if PRINT_FULL_SORTED:
        print("\nFULL ORDER BY ALL (desc) on successful set:")
        for i, r in enumerate(sort_all, 1):
            print(f"{i:02d}. {r['name']} | {r['universe']}  all={r['all']:.3f}  psy={r['psy']:.3f}  orig={r['orig']:.3f}")

        print("\nFULL ORDER BY PSY (desc) on successful set:")
        for i, r in enumerate(sort_psy, 1):
            print(f"{i:02d}. {r['name']} | {r['universe']}  psy={r['psy']:.3f}  all={r['all']:.3f}  orig={r['orig']:.3f}")

    # ---- В виде питон-списков (удобно вставлять в презентацию/код) ----
    ALL_ORDER = [[r["name"], r["universe"]] for r in top_all_order]
    PSY_ORDER = [[r["name"], r["universe"]] for r in top_psy_order]
    print("\nAS PYTHON LISTS (TOP-10):")
    print("ALL_ORDER =", ALL_ORDER)
    print("PSY_ORDER =", PSY_ORDER)

    if bad:
        print(f"\nNote: failed/partial API responses ignored: {len(bad)}")
