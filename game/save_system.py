"""Versioned portable JSON save; browser persistence, never shared server files."""

import copy
import json
import math

SAVE_VERSION = 1


class SaveError(ValueError):
    pass


def number(value, low, high):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        raise SaveError("Valor fuera de rango")
    return value


def validate_state(state):
    from .nivel import level_config
    from .estadisticas import new_stats
    from .dificultad import DIFFICULTIES

    if not isinstance(state, dict) or state.get("difficulty") not in DIFFICULTIES:
        raise SaveError("Partida incompatible")
    if not isinstance(state.get("name"), str) or not 1 <= len(state["name"]) <= 24:
        raise SaveError("Nombre inválido")
    if state.get("checkpoint") not in ["inicio", "arena", "final"]:
        raise SaveError("Checkpoint inválido")
    level = level_config(state["difficulty"])
    grid = level["grid"]
    p = state["player"]
    number(p["x"], 1, 26.99)
    number(p["y"], 1, 13.99)
    number(p["angle"], -100000, 100000)
    if grid[int(p["y"])][int(p["x"])] in (1, 2):
        raise SaveError("Posición inválida")
    number(p["hp"], 0, 100)
    number(p["armor"], 0, 100)
    for key in new_stats():
        number(state["stats"][key], 0, 1e9)
    if state["stats"]["correct"] > state["stats"]["attempted"]:
        raise SaveError("Estadísticas inválidas")
    if (
        not isinstance(state["weapons"], dict)
        or "pistol" not in state["weapons"]
        or set(state["weapons"]) - {"pistol", "shotgun"}
    ):
        raise SaveError("Armas inválidas")
    for key, weapon in state["weapons"].items():
        number(weapon["loaded"], 0, 12 if key == "pistol" else 8)
        number(weapon["reserve"], 0, 999)
        number(weapon["mods"], 0, 1)
    if state["weapon"] not in state["weapons"]:
        raise SaveError("Arma no disponible")
    for key in ["mad_used", "door_open", "terminal_used", "cache_used", "complete"]:
        if not isinstance(state["progress"][key], bool):
            raise SaveError("Progreso inválido")
    valid_ids = {e["id"] for e in level["enemies"]}
    if (
        len(state["enemies"]) != len(valid_ids)
        or {e["id"] for e in state["enemies"]} != valid_ids
    ):
        raise SaveError("Enemigos inválidos")
    for e in state["enemies"]:
        if e["type"] not in ["worker", "crawler", "rivet"]:
            raise SaveError("Tipo inválido")
        number(e["x"], 0, 28)
        number(e["y"], 0, 15)
        number(e["hp"], 0, 100)
    if (
        not isinstance(state["collected"], list)
        or len(state["collected"]) > 30
        or set(state["collected"]) - {i["id"] for i in level["items"]}
    ):
        raise SaveError("Recursos inválidos")
    return copy.deepcopy(state)


def make_save(state, checkpoint):
    return {
        "version": SAVE_VERSION,
        "state": copy.deepcopy(state),
        "checkpoint_state": copy.deepcopy(checkpoint),
    }


def load_save(data):
    try:
        if len(json.dumps(data, ensure_ascii=False)) > 120000:
            raise SaveError("Archivo demasiado grande")
        if isinstance(data, str):
            if len(data) > 100000:
                raise SaveError("Archivo demasiado grande")
            data = json.loads(data)
        if data["version"] != SAVE_VERSION:
            raise SaveError("Versión de guardado incompatible")
        state = validate_state(data["state"])
        checkpoint = validate_state(data["checkpoint_state"])
        if (
            state["difficulty"] != checkpoint["difficulty"]
            or state["name"] != checkpoint["name"]
        ):
            raise SaveError("Checkpoint incompatible")
        return state, checkpoint
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SaveError("Guardado inválido o incompatible") from exc
