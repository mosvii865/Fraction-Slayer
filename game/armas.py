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
    "sniper": {
        "name": "SNIPER RIFLE", "damage": 145, "range": 22, "spread": 0.032,
        "capacity": 5, "cooldown": 1.05, "reload": 2.15, "max_mods": 4,
    },
    "lmg": {
        "name": "LMG", "damage": 18, "range": 14.5, "spread": 0.10,
        "capacity": 60, "cooldown": 0.085, "reload": 2.75, "max_mods": 4,
    },
    "rocket": {
        "name": "ROCKET LAUNCHER", "damage": 220, "range": 18, "spread": 0.035,
        "capacity": 1, "cooldown": 1.15, "reload": 2.65, "max_mods": 4,
        "projectile_speed": 6.0, "blast_radius": 2.6,
    },
    "el_toro": {
        "name": "EL TORO", "damage": 520, "range": 20, "spread": 0.025,
        "capacity": 1, "cooldown": 1.8, "reload": 3.0, "max_mods": 0,
        "blast_radius": 2.0,
    },
}
FUTURE_WEAPONS = []


def weapon_config(weapon, mods=0):
    """Return current weapon stats after the campaign upgrades implemented so far.

    Laboratory unlocks MOD II; Foundry unlocks MOD III. The save shape remains
    the same, so older campaign saves remain portable.
    """
    data = deepcopy(WEAPONS[weapon])
    if mods >= 1:
        if weapon == "pistol":
            data.update(damage=data["damage"] * 1.15, spread=0.055)
        elif weapon == "shotgun":
            data.update(spread=0.14, range=10)
        elif weapon == "assault":
            data.update(spread=0.045, range=15)
        elif weapon == "sawed_off":
            data.update(damage=data["damage"] * 1.18, spread=0.30)
        elif weapon == "sniper":
            data.update(spread=0.016, range=24)
        elif weapon == "lmg":
            data.update(spread=0.075, range=15)
        elif weapon == "rocket":
            data.update(projectile_speed=7.0)
    if mods >= 2:
        if weapon == "pistol":
            data.update(capacity=18)
        elif weapon == "shotgun":
            data.update(cooldown=0.70, reload=1.75)
        elif weapon == "assault":
            data.update(capacity=40)
        elif weapon == "sawed_off":
            data.update(reload=1.55)
        elif weapon == "sniper":
            data.update(spread=0.009, range=27, reload=1.9)
        elif weapon == "lmg":
            data.update(capacity=75, reload=2.5)
        elif weapon == "rocket":
            data.update(blast_radius=2.9, reload=2.35)

    if mods >= 3:
        if weapon == "pistol":
            data.update(cooldown=0.24, reload=0.95)
        elif weapon == "shotgun":
            data.update(capacity=10)
        elif weapon == "assault":
            data.update(damage=data["damage"] * 1.12, cooldown=0.105)
        elif weapon == "sawed_off":
            data.update(cooldown=0.78, damage=data["damage"] * 1.08)
        elif weapon == "sniper":
            data.update(damage=data["damage"] * 1.15, range=29)
        elif weapon == "lmg":
            data.update(capacity=90)
        elif weapon == "rocket":
            data.update(blast_radius=3.2)
    return data
