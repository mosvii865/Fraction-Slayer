from copy import deepcopy

WEAPONS = {
    "pistol": {
        "name": "PISTOLA",
        "damage": 24,
        "range": 13,
        "spread": 0.09,
        "capacity": 12,
        "cooldown": 0.3,
        "reload": 1.1,
        "max_mods": 4,
    },
    "shotgun": {
        "name": "ESCOPETA DE CORREDERA",
        "damage": 80,
        "range": 7,
        "spread": 0.24,
        "capacity": 8,
        "cooldown": 0.85,
        "reload": 1.9,
        "max_mods": 4,
    },
}
FUTURE_WEAPONS = ["sawed_off", "sniper", "assault", "lmg", "rocket", "el_toro"]


def weapon_config(weapon, mods=0):
    data = deepcopy(WEAPONS[weapon])
    if mods:
        if weapon == "pistol":
            data.update(damage=data["damage"] * 1.15, spread=0.055)
        else:
            data.update(spread=0.14, range=10)
    return data
