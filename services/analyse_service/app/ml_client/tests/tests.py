import os
import sys
from pathlib import Path
import numpy as np
import pytest
from sklearn.metrics import roc_auc_score, average_precision_score

# ---- your knobs ----
TOPK_FRAC = 0.10
MIN_LIFT_AT_K = 1.05
MAX_MAE_BASELINE_MULT = 1.00
MIN_P_STD = 1e-4
MIN_MID_FRAC = 0.01
N_BINS = 10
MAX_ECE = 0.25

MIN_SPREAD_FRAC = 0.05
SPREAD_THRESH = 0.10

# ---- config ----
FEATURE = "flag_serious_violent_crime"
GROUPS = ["all", "appearance", "profession", "psycho", "stat"]

# add project root to sys.path (so "import app" works even if pytest runs weird)
HERE = Path(__file__).resolve()
PROJ = HERE
for _ in range(8):
    if (PROJ / "app").exists():
        break
    PROJ = PROJ.parent
if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from app.db import DBGet
from app.ml_client.ml_entities import CharactersList
from app.ml_client.ml_file_control import load_model
from app.ml_client.ml_config import MODEL_DIR, VERSION


def _model_path(group: str) -> Path:
    ml_client_dir = Path(__file__).resolve().parents[1]
    base = ml_client_dir / MODEL_DIR
    p1 = base / f"v_{VERSION}" / group / f"model_{FEATURE}.joblib"
    p2 = base / group / f"model_{FEATURE}.joblib"
    return p1 if p1.exists() else p2


@pytest.fixture(scope="session")
def dataset():
    profiles = DBGet().get_all_characters()
    cl = CharactersList(profiles)
    X_full = np.array(cl.clear_matrix, dtype=float)
    order_full = list(cl.guarantor)
    idx = {name: i for i, name in enumerate(order_full)}
    return X_full, order_full, idx


def _ece(y01: np.ndarray, p: np.ndarray, n_bins: int) -> float:
    p = np.clip(p.astype(float), 0.0, 1.0)
    y01 = y01.astype(int)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(p)
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        m = (p >= lo) & (p < hi if i < n_bins - 1 else p <= hi)
        cnt = int(np.sum(m))
        if cnt == 0:
            continue
        acc = float(np.mean(y01[m]))
        conf = float(np.mean(p[m]))
        ece += (cnt / n) * abs(acc - conf)
    return float(ece)


def _metrics(y01: np.ndarray, p: np.ndarray) -> dict:
    p = np.clip(p.astype(float), 0.0, 1.0)
    y01 = y01.astype(int)

    base = float(np.mean(y01))
    mae = float(np.mean(np.abs(p - y01)))
    mae_base = float(np.mean(np.abs(base - y01)))

    n = len(y01)
    k = max(1, int(round(n * TOPK_FRAC)))
    top = np.argsort(-p)[:k]
    prec_k = float(np.mean(y01[top]))
    lift_k = float(prec_k / max(1e-12, base))

    p_std = float(np.std(p))

    mid_lo, mid_hi = 1.0 / N_BINS, 1.0 - 1.0 / N_BINS
    mid_frac = float(np.mean((p > mid_lo) & (p < mid_hi)))

    ece = _ece(y01, p, N_BINS)

    if len(np.unique(y01)) > 1:
        roc = float(roc_auc_score(y01, p))
        pr = float(average_precision_score(y01, p))
    else:
        roc = float("nan")
        pr = float("nan")

    return {
        "base": base,
        "mae": mae,
        "mae_base": mae_base,
        "lift@k": lift_k,
        "p_std": p_std,
        "mid_frac": mid_frac,
        "ece": ece,
        "roc_auc": roc,
        "pr_auc": pr,
    }


def _predict_all_rows(payload: dict, X_full: np.ndarray, idx: dict) -> np.ndarray:
    model = payload["model"]
    order_used = list(payload["order"])
    target_idx_sliced = int(payload["feature_pos"])
    fill_value = float(payload["fill_value"])

    col_idxs = [idx[name] for name in order_used]
    X = X_full[:, col_idxs].copy()
    X[:, target_idx_sliced] = fill_value

    oob = getattr(model, "oob_prediction_", None)
    if oob is not None:
        p = np.array(oob, dtype=float)
    else:
        p = np.array(model.predict(X), dtype=float)

    return np.clip(p, 0.0, 1.0)


@pytest.mark.parametrize("group", GROUPS)
def test_model_quality(group: str, dataset):
    mp = _model_path(group)
    if not mp.exists():
        pytest.skip(f"Model not trained: {mp}")

    X_full, _, idx = dataset
    assert FEATURE in idx

    payload = load_model(str(mp))
    y = X_full[:, idx[FEATURE]]
    y01 = (y >= 0.5).astype(int)

    p = _predict_all_rows(payload, X_full, idx)
    m = _metrics(y01, p)

    assert m["p_std"] >= MIN_P_STD
    assert m["mid_frac"] >= MIN_MID_FRAC
    assert m["ece"] <= MAX_ECE
    assert m["mae"] <= m["mae_base"] * MAX_MAE_BASELINE_MULT
    assert m["lift@k"] >= MIN_LIFT_AT_K

    if len(np.unique(y01)) > 1:
        assert m["pr_auc"] >= m["base"]


@pytest.mark.parametrize("group", GROUPS)
def test_permutation_kills_signal(group: str, dataset):
    mp = _model_path(group)
    if not mp.exists():
        pytest.skip(f"Model not trained: {mp}")

    X_full, _, idx = dataset
    payload = load_model(str(mp))

    y = X_full[:, idx[FEATURE]]
    y01 = (y >= 0.5).astype(int)

    p = _predict_all_rows(payload, X_full, idx)

    rng = np.random.default_rng(12345)
    y_shuf = rng.permutation(y01)

    m = _metrics(y_shuf, p)

    assert m["lift@k"] <= 1.05
    if len(np.unique(y_shuf)) > 1:
        assert m["pr_auc"] <= float(np.mean(y_shuf)) + 0.05


def test_group_spread_nonzero(dataset):
    X_full, _, idx = dataset

    paths = {g: _model_path(g) for g in GROUPS}
    for g, p in paths.items():
        if not p.exists():
            pytest.skip(f"Model not trained: {p}")

    payloads = {g: load_model(str(paths[g])) for g in GROUPS}

    rng = np.random.default_rng(777)
    n = X_full.shape[0]
    sample_n = min(400, n)
    rows = rng.choice(n, size=sample_n, replace=False)

    preds = []
    for g in GROUPS:
        p_all = _predict_all_rows(payloads[g], X_full, idx)
        preds.append(p_all[rows])

    preds = np.vstack(preds)  # (G, sample_n)
    spread = np.max(preds, axis=0) - np.min(preds, axis=0)

    frac = float(np.mean(spread >= SPREAD_THRESH))
    assert frac >= MIN_SPREAD_FRAC


@pytest.mark.parametrize("group", GROUPS)
def test_print_metrics(group: str, dataset, capsys):
    mp = _model_path(group)
    if not mp.exists():
        pytest.skip(f"Model not trained: {mp}")

    X_full, _, idx = dataset
    payload = load_model(str(mp))

    y = X_full[:, idx[FEATURE]]
    y01 = (y >= 0.5).astype(int)

    p = _predict_all_rows(payload, X_full, idx)
    m = _metrics(y01, p)

    oob_mae = payload.get("oob_mae", None)
    line = {
        "group": group,
        "base": round(m["base"], 3),
        "mae": round(m["mae"], 3),
        "mae_base": round(m["mae_base"], 3),
        "lift@k": round(m["lift@k"], 3),
        "pr_auc": None if np.isnan(m["pr_auc"]) else round(m["pr_auc"], 3),
        "roc_auc": None if np.isnan(m["roc_auc"]) else round(m["roc_auc"], 3),
        "ece": round(m["ece"], 3),
        "p_std": round(m["p_std"], 5),
        "mid_frac": round(m["mid_frac"], 3),
        "oob_mae": None if oob_mae is None else round(float(oob_mae), 3),
    }
    print(line)
