from pathlib import Path

VERSION = 2 # last liquid version of model
BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "ml_client/ml_models" / f"v_{VERSION}"
SEED = 42
N_ESTIMATORS = 3000
FEATURE_NAME = "flag_serious_violent_crime"


BASE_DIR = Path(__file__).resolve().parent  # app/ml_client/
MEDIANS_PATH = str((BASE_DIR / "data" / "medians.json").resolve())

AVOID = [
    "flag_war_criminal",
    "flag_killer",
    "flag_thief",
    "flag_organized_crime",
    # "flag_pacifist",
    # "flag_moralist",
    "flag_woke",
    "age_mental",
    "age_physical",
    "name",
    "universe",
    # "profession_criminal" # to avoid 1 to 1 situation
]

DROP_P = 0.15
RF_MAX_DEPTH = 30
RF_MIN_LEAF = 5