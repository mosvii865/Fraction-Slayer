from .armas import weapon_config, WEAPONS

MODS = {"pistol": "Precision Barrel", "shotgun": "Tight Choke"}


def eligible_weapons(state, mod=1):
    return [
        w
        for w, a in state["weapons"].items()
        if w in MODS and a["mods"] == mod - 1 and mod <= 1
    ]


def apply_upgrade(state, weapon, mod=1):
    if weapon not in WEAPONS or weapon not in eligible_weapons(state, mod):
        raise ValueError("No hay mejora válida para esta arma")
    state["weapons"][weapon]["mods"] = mod
    return weapon_config(weapon, mod)
