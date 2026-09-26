from copy import deepcopy

WEAPONS = {
    "pistol": {
        "name": "PISTOLA", "damage": 24, "range": 13, "spread": 0.09,
        "capacity": 12, "cooldown": 0.3, "reload": 1.1, "max_mods": 4,
    },
    "shotgun": {
        "name": "ESCOPETA DE CORREDERA", "damage": 80, "range": 7, "spread": 0.24,
        "capacity": 8, "cooldown": 0.85, "reload": 1.9, "max_mods": 4,
    },
    "assault": {
        "name": "ASSAULT RIFLE", "damage": 21, "range": 14, "spread": 0.075,
        "capacity": 30, "cooldown": 0.115, "reload": 1.55, "max_mods": 4,
    },
    "sawed_off": {
        "name": "SAWED-OFF", "damage": 125, "range": 5.2, "spread": 0.34,
        "capacity": 2, "cooldown": 1.0, "reload": 2.2, "max_mods": 4,
    },
}
FUTURE_WEAPONS = ["sniper", "lmg", "rocket", "el_toro"]


def weapon_config(weapon, mods=0):
    data = deepcopy(WEAPONS[weapon])
    if mods:
        if weapon == "pistol":
            data.update(damage=data["damage"] * 1.15, spread=0.055)
        elif weapon == "shotgun":
            data.update(spread=0.14, range=10)
        elif weapon == "assault":
            data.update(spread=0.045, range=15)
        elif weapon == "sawed_off":
            data.update(damage=data["damage"] * 1.18, spread=0.30)
    return data
