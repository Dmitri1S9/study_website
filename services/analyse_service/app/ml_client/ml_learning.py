import logging
import os
from typing import List

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from app.ml_client.ml_config import VERSION, MODEL_DIR, FEATURE_NAME, SEED, N_ESTIMATORS, DROP_P, RF_MAX_DEPTH, \
    RF_MIN_LEAF
from app.db import DBGet
from app.ml_client.ml_entities import CharactersList
from app.ml_client.ml_file_control import save_model
from app.ml_client.ml_scripts import (
    mesh_psycho, mesh_appearance, mesh_stat, mesh_profession, mesh_all,
    slice_by_mesh
)

log = logging.getLogger(__name__)


def apply_feature_dropout(matrix: np.ndarray, drop_p: float, seed: int, skip_col: int) -> np.ndarray:
    if drop_p <= 0:
        return matrix
    rng = np.random.default_rng(seed)
    med = np.median(matrix, axis=0)

    mask = rng.random(matrix.shape) < drop_p
    mask[:, skip_col] = False
    X2 = matrix.copy()
    X2[mask] = med[np.where(mask)[1]]
    return X2


class MLLearnContext:
    def __init__(self) -> None:
        self.log = log
        self.db_get = DBGet()
        self.characters_list = self.db_get.get_all_characters()[:1997]


class MLTraining(MLLearnContext):
    def __init__(self) -> None:
        super().__init__()
        self.cl = CharactersList(self.characters_list)
        self.order: List[str] = self.cl.guarantor
        self.CLEAR: np.ndarray = np.array(self.cl.clear_matrix, dtype=float)

    def _get_fill_value(self, target_idx: int) -> float:
        return float(np.median(self.CLEAR[:, target_idx]))

    def train_param(self, feature_pos_: int, seed: int, n_estimators: int, mesh_func, group_name: str = "all"):
        if feature_pos_ < 0 or feature_pos_ >= self.CLEAR.shape[1]:
            raise ValueError(f"feature_pos out of range: {feature_pos_} (0..{self.CLEAR.shape[1] - 1})")

        x_matrix, order_used, target_idx = slice_by_mesh(feature_pos_, mesh_func, self.order, self.CLEAR)

        fill_value = self._get_fill_value(feature_pos_)
        x_matrix[:, target_idx] = fill_value

        x_matrix = apply_feature_dropout(x_matrix, DROP_P, seed, target_idx)

        y = self.CLEAR[:, feature_pos_].astype(float)

        model_ = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=seed,
            n_jobs=-1,
            bootstrap=True,
            oob_score=True,
            max_depth=RF_MAX_DEPTH,
            min_samples_leaf=RF_MIN_LEAF,

        )
        model_.fit(x_matrix, y)

        oob = getattr(model_, "oob_prediction_", None)
        oob_mae = None
        if oob is not None:
            oob = np.clip(oob.astype(float), 0.0, 1.0)
            oob_mae = float(np.mean(np.abs(oob - y)))

        os.makedirs(MODEL_DIR, exist_ok=True)
        group_dir = os.path.join(MODEL_DIR, group_name)
        os.makedirs(group_dir, exist_ok=True)

        feature_name = self.order[feature_pos_]
        base_rate = float(np.mean(y))
        save_model(
            path=os.path.join(MODEL_DIR, group_name, f"model_{feature_name}.joblib"),
            model_=model_,
            feature_pos=target_idx,
            order_=order_used,
            fill_value=fill_value,
            seed=seed,
            base_rate=base_rate,
            n_estimators=n_estimators,
            drop_p=DROP_P,
            rf_max_depth=RF_MAX_DEPTH,
            rf_min_leaf=RF_MIN_LEAF,
            oob_mae=oob_mae,
        )

    def train_param_on_all(self, feature_pos_: int, seed: int, n_estimators: int):
        self.train_param(feature_pos_=feature_pos_, seed=seed, n_estimators=n_estimators, mesh_func=mesh_all)

    def train_param_on_groups(self, feature_pos_: int, seed: int, n_estimators: int):
        for name, func in {
            "psycho": mesh_psycho, "appearance": mesh_appearance, "stat": mesh_stat, "profession": mesh_profession
        }.items():
            self.train_param(feature_pos_=feature_pos_, seed=seed, n_estimators=n_estimators, mesh_func=func, group_name=name)


if __name__ == "__main__":
    ctx = MLTraining()
    feature_pos = ctx.order.index(FEATURE_NAME)

    ctx.train_param_on_groups(feature_pos_=feature_pos, seed=SEED, n_estimators=N_ESTIMATORS)
    ctx.train_param_on_all(feature_pos_=feature_pos, seed=SEED, n_estimators=N_ESTIMATORS)