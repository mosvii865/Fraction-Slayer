"""Versioned portable JSON; no cross-level or cross-run checkpoint mixing."""

import copy
import json
import math
from .nivel import level_config
from .armas import WEAPONS
from .estadisticas import new_stats
from .world import solid, initial_progress

SAVE_VERSION = 2


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
    s = copy.deepcopy(state)
    if not isinstance(s, dict):
        raise SaveError("Partida incompatible")
    level = level_config(s["difficulty"], s["level_id"])
    if s["level_revision"] != level["revision"]:
        raise SaveError("Revisión de nivel incompatible")
    if not isinstance(s["name"], str) or not 1 <= len(s["name"]) <= 24:
        raise SaveError("Nombre inválido")
    if not isinstance(s["run_id"], str) or not s["run_id"]:
        raise SaveError("Partida inválida")
    if s["checkpoint"] not in {c["id"] for c in level["checkpoints"]}:
        raise SaveError("Checkpoint inválido")
    template = initial_progress(level)
    for key in ("stations", "doors", "objectives", "triggers", "waves", "secrets"):
        if set(s["progress"][key]) != set(template[key]) or any(
            type(v) is not bool for v in s["progress"][key].values()
        ):
            raise SaveError("Progreso inválido")
    if type(s["progress"]["complete"]) is not bool:
        raise SaveError("Progreso inválido")
    utcj = s["progress"]["utcj_found"]
    if (
        not isinstance(utcj, list)
        or len(utcj) != len(set(utcj))
        or any(
            i not in {x["id"] for x in level["secrets"] if x["kind"] == "utcj"}
            or not s["progress"]["secrets"][i]
            for i in utcj
        )
    ):
        raise SaveError("Secretos inválidos")
    times = s["progress"].get("trigger_times", {})
    if not isinstance(times, dict) or set(times) - set(template["triggers"]):
        raise SaveError("Tiempos de eventos inválidos")
    for ident, timestamp in times.items():
        number(timestamp, 0, s["stats"]["seconds"])
        if not s["progress"]["triggers"][ident]:
            raise SaveError("Evento no activado")
    p = s["player"]
    number(p["x"], 0, level["width"] - 1e-6)
    number(p["y"], 0, level["height"] - 1e-6)
    if solid(level, s["progress"], p["x"], p["y"]):
        raise SaveError("Posición inválida")
    number(p["angle"], -1e5, 1e5)
    number(p["hp"], 0, level["player_config"]["max_hp"])
    number(p["armor"], 0, level["player_config"]["max_armor"])
    number(p.get("grace", 0), 0, level["respawn_rules"]["grace"])
    for key in new_stats():
        number(s["stats"][key], 0, 1e9)
    if s["stats"]["correct"] > s["stats"]["attempted"]:
        raise SaveError("Estadísticas inválidas")
    if (
        not isinstance(s["weapons"], dict)
        or not s["weapons"]
        or set(s["weapons"]) - set(WEAPONS)
    ):
        raise SaveError("Armas inválidas")
    for w, a in s["weapons"].items():
        for k, maximum in [
            ("loaded", WEAPONS[w]["capacity"]),
            ("reserve", 999),
            ("mods", 1),
        ]:
            number(a[k], 0, maximum)
            if not isinstance(a[k], int):
                raise SaveError("Inventario inválido")
    if s["weapon"] not in s["weapons"]:
        raise SaveError("Arma no disponible")
    original = {e["id"]: e for e in level["enemies"]}
    if len(s["enemies"]) != len(original) or {e["id"] for e in s["enemies"]} != set(
        original
    ):
        raise SaveError("Enemigos inválidos")
    for e in s["enemies"]:
        if (
            e["type"] != original[e["id"]]["type"]
            or e["group"] != original[e["id"]]["group"]
            or type(e["active"]) is not bool
        ):
            raise SaveError("Tipo de enemigo inválido")
        number(e["hp"], 0, level["enemy_types"][e["type"]]["hp"])
        number(e["x"], 0, level["width"] - 1e-6)
        number(e["y"], 0, level["height"] - 1e-6)
        number(e["facing"], -1e5, 1e5)
        number(e["search_time"], 0, 60)
        number(e["stun_time"], 0, 60)
        if (
            e["ai_state"]
            not in ("idle", "pursuing", "searching", "stunned", "charging", "preparing", "slamming", "recovering")
            or e["charge_state"] not in ("idle", "charging", "blocked", "preparing", "slamming", "recovering")
            or type(e["charge_blocked"]) is not bool
        ):
            raise SaveError("Estado IA inválido")
        if e["type"] == "loader":
            for key in ("phase_time", "cooldown"):
                number(e.get(key, 0), 0, 60)
            number(e.get("attack_index", 0), 0, 1000000)
        if e.get("last_known") is not None:
            number(e["last_known"]["x"], 0, level["width"])
            number(e["last_known"]["y"], 0, level["height"])
    collected = s["collected"]
    if (
        not isinstance(collected, list)
        or len(collected) != len(set(collected))
        or set(collected) - {i["id"] for i in level["items"]}
    ):
        raise SaveError("Recursos inválidos")
    if set(s["inventory"]) != {"quest_items", "key_items"}:
        raise SaveError("Inventario inválido")
    for bag in s["inventory"].values():
        if not isinstance(bag, dict) or len(bag) > 256:
            raise SaveError("Inventario inválido")
        for key, n in bag.items():
            if not isinstance(key, str) or not 1 <= len(key) <= 100:
                raise SaveError("Objeto inválido")
            number(n, 0, 999)
    report = s.get("report")
    if not isinstance(report, dict) or any(
        not isinstance(report.get(k), list)
        for k in ("observations", "incidents", "measurements", "project_utcj")
    ):
        raise SaveError("Reporte inválido")
    return s


def make_save(state, checkpoint):
    return dict(
        version=SAVE_VERSION,
        level_id=state["level_id"],
        state=copy.deepcopy(state),
        checkpoint_state=copy.deepcopy(checkpoint),
    )


def load_save(data):
    try:
        if len(json.dumps(data, ensure_ascii=False)) > 500000:
            raise SaveError("Archivo demasiado grande")
        if isinstance(data, str):
            data = json.loads(data)
        if data["version"] != SAVE_VERSION:
            raise SaveError(
                "Versión de guardado incompatible. Inicia una partida nueva."
            )
        state = validate_state(data["state"])
        checkpoint = validate_state(data["checkpoint_state"])
        if data["level_id"] != state["level_id"] or any(
            state[k] != checkpoint[k]
            for k in ("level_id", "level_revision", "difficulty", "name", "run_id")
        ):
            raise SaveError("Checkpoint de otra partida o nivel")
        return state, checkpoint
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SaveError(
            f"Guardado inválido o incompatible: {exc}. Puedes iniciar una partida nueva."
        ) from exc
