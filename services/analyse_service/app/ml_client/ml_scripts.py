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
