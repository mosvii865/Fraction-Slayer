"""Shared Python progression, interaction and safety primitives."""

import math
from copy import deepcopy
from .armas import WEAPONS
from .dificultad import get_difficulty
from .mejoras import apply_upgrade


def entity(level, collection, ident):
    item = next((x for x in level[collection] if x["id"] == ident), None)
    if item is None:
        raise ValueError(f"{collection}: entidad inexistente ({ident})")
    return item


def solid(level, progress, x, y):
    if not 0 <= x < level["width"] or not 0 <= y < level["height"]:
        return True
    cell = level["grid"][int(y)][int(x)]
    if cell == 3:
        door = next((d for d in level["doors"] if d["cell"] == [int(x), int(y)]), None)
        return not door or not progress["doors"].get(door["id"], False)
    return cell != 0


def clear_line(level, state, a, b):
    n = max(1, math.ceil(math.hypot(b["x"] - a["x"], b["y"] - a["y"]) * 10))
    return all(
        not solid(
            level,
            state["progress"],
            a["x"] + (b["x"] - a["x"]) * i / n,
            a["y"] + (b["y"] - a["y"]) * i / n,
        )
        for i in range(n + 1)
    )


def in_zone(p, z):
    return z[0] <= p["x"] <= z[2] and z[1] <= p["y"] <= z[3]


def condition(rule, state, level, event=None):
    if not rule:
        return True
    if "all" in rule:
        return all(condition(r, state, level, event) for r in rule["all"])
    if "any" in rule:
        return any(condition(r, state, level, event) for r in rule["any"])
    if "zone" in rule:
        return in_zone(state["player"], rule["zone"])
    if "event" in rule:
        return rule["event"] == event
    for key, collection in [
        ("objective", "objectives"),
        ("door_open", "doors"),
        ("station_used", "stations"),
        ("trigger", "triggers"),
        ("wave", "waves"),
        ("secret", "secrets"),
    ]:
        if key in rule:
            return state["progress"][collection].get(rule[key], False)
    if "item" in rule:
        return any(bag.get(rule["item"], 0) > 0 for bag in state["inventory"].values())
    if "group_defeated" in rule:
        group = [e for e in state["enemies"] if e["group"] == rule["group_defeated"]]
        return bool(group) and all(e["hp"] <= 0 for e in group)
    raise ValueError("Condición desconocida")


def unsafe(level, state, point=None, checkpoint=False):
    p = point or state["player"]
    for e in state["enemies"]:
        if not e["active"] or e["hp"] <= 0:
            continue
        distance = math.hypot(p["x"] - e["x"], p["y"] - e["y"])
        if checkpoint and distance < 2:
            return True
        if distance < (
            max(6, level["enemy_types"][e["type"]]["range"] + 0.5) if checkpoint else 6
        ) and clear_line(level, state, p, e):
            # Nearby visible enemies acquire the player immediately in realtime.
            return True
    return False


def initial_progress(level):
    return {
        **{
            k: {e["id"]: False for e in level[k]}
            for k in ("stations", "doors", "triggers", "waves", "objectives", "secrets")
        },
        "utcj_found": [],
        "complete": False,
    }


def pickup(state, item, level):
    """Validate dispatch before mutation/collected. Caller commits candidate atomically."""
    t = item["type"]
    n = item.get("amount", 1)
    if t not in (
        "ammo",
        "health",
        "armor",
        "weapon",
        "quest_item",
        "key_item",
        "secret_item",
    ):
        raise ValueError("Tipo de pickup desconocido")
    if not isinstance(n, (int, float)) or not 0 < n <= 999:
        raise ValueError("Cantidad inválida")
    if t in ("ammo", "weapon"):
        w = item["weapon"]
        if w not in WEAPONS:
            raise ValueError("Arma inválida")
        if t == "ammo":
            if w not in state["weapons"]:
                raise ValueError("Arma no disponible")
            state["weapons"][w]["reserve"] = min(
                999, state["weapons"][w]["reserve"] + n
            )
        elif w not in state["weapons"]:
            state["weapons"][w] = dict(
                loaded=WEAPONS[w]["capacity"],
                reserve=get_difficulty(state["difficulty"]).get(w + "_reserve", 0),
                mods=0,
            )
    elif t in ("health", "armor"):
        field = "hp" if t == "health" else "armor"
        state["player"][field] = min(
            level["player_config"]["max_" + field], state["player"][field] + n
        )
    elif t in ("quest_item", "key_item"):
        key = item["item_id"]
        if not isinstance(key, str) or not key:
            raise ValueError("Objeto inválido")
        bag = state["inventory"]["quest_items" if t == "quest_item" else "key_items"]
        bag[key] = bag.get(key, 0) + n
    else:
        discover_secret(state, level, item["secret_id"])


def discover_secret(state, level, ident):
    secret = entity(level, "secrets", ident)
    if state["progress"]["secrets"][ident]:
        return
    state["progress"]["secrets"][ident] = True
    state["stats"]["secrets"] += 1
    if secret["kind"] == "utcj":
        state["progress"]["utcj_found"].append(ident)
        state["report"]["project_utcj"].append(ident)


def rewards(state, level, items, weapon=None):
    candidate = deepcopy(state)
    for reward in items:
        t = reward["type"]
        if t == "upgrade":
            apply_upgrade(
                candidate, weapon or reward.get("weapon"), reward.get("mod", 1)
            )
        elif t == "door":
            entity(level, "doors", reward["id"])
            candidate["progress"]["doors"][reward["id"]] = True
        elif t == "objective":
            entity(level, "objectives", reward["id"])
            candidate["progress"]["objectives"][reward["id"]] = True
        elif t == "secret":
            discover_secret(candidate, level, reward["id"])
        elif t == "consume_item":
            bag = candidate["inventory"][reward.get("bag", "quest_items")]
            key = reward["item_id"]
            n = reward.get("amount", 1)
            if bag.get(key, 0) < n:
                raise ValueError("Falta objeto requerido")
            bag[key] -= n
        elif t == "ensure_ammo":
            for w, n in reward["minimum"].items():
                if w not in WEAPONS or n < 0:
                    raise ValueError("Reserva mínima inválida")
                if w in candidate["weapons"]:
                    a = candidate["weapons"][w]
                    a["reserve"] = max(a["reserve"], n - a["loaded"])
        else:
            pickup(candidate, reward, level)
    return candidate


def advance(state, level, event=None):
    # Finite monotonic flags; revisit dependencies until stable.
    for _ in range(len(level["objectives"]) + len(level["triggers"]) + 1):
        changed = False
        for obj in level["objectives"]:
            if (
                not state["progress"]["objectives"][obj["id"]]
                and obj.get("condition")
                and condition(obj["condition"], state, level, event)
            ):
                state["progress"]["objectives"][obj["id"]] = True
                changed = True
        for trigger in level["triggers"]:
            if state["progress"]["triggers"][trigger["id"]] or not condition(
                trigger["condition"], state, level, event
            ):
                continue
            for action in trigger["actions"]:
                if action["type"] in ("activate_group", "activate_wave"):
                    if action["type"] == "activate_wave":
                        wave = entity(level, "waves", action["id"])
                        groups = wave["groups"]
                        state["progress"]["waves"][wave["id"]] = True
                        state = rewards(state, level, wave.get("rewards", []))
                    else:
                        groups = [action["id"]]
                    for enemy in state["enemies"]:
                        if enemy["group"] in groups:
                            enemy["active"] = True
                else:
                    state = rewards(state, level, [action])
            state["progress"]["triggers"][trigger["id"]] = True
            changed = True
        if not changed:
            break
    return state
