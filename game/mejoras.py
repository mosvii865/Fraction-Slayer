from .armas import weapon_config, WEAPONS

MODS = {
    "pistol": {1: "Precision Barrel", 2: "Extended Magazine", 3: "Quick Action"},
    "shotgun": {1: "Tight Choke", 2: "Reinforced Pump", 3: "Extended Tube"},
    "assault": {1: "Compensator", 2: "Extended Magazine", 3: "Combat Receiver"},
    "sawed_off": {1: "Magnum Load", 2: "Automatic Ejector", 3: "Twin Trigger"},
    "sniper": {1: "Stabilized Scope", 2: "Variable Optics", 3: "Armor Piercing"},
    "lmg": {1: "Recoil Dampener", 2: "Heavy Box", 3: "Feed Optimizer"},
    "rocket": {1: "Stabilized Rocket", 2: "Expanded Blast", 3: "Demolition Chamber"},
}


def mod_name(weapon, mod):
    return MODS.get(weapon, {}).get(mod, f"MOD {mod}")


def eligible_weapons(state, mod=1):
    """Weapons eligible for an exact target MOD level."""
    return [
        w for w, a in state["weapons"].items()
        if w in MODS and a["mods"] == mod - 1 and mod in MODS[w]
    ]


def eligible_next_weapons(state, max_mod=2):
    """Weapons that can receive their next sequential campaign upgrade."""
    result = []
    for w, a in state["weapons"].items():
        next_mod = a["mods"] + 1
        if w in MODS and next_mod <= max_mod and next_mod in MODS[w]:
            result.append(w)
    return result


def apply_upgrade(state, weapon, mod=1):
    if weapon not in WEAPONS or weapon not in eligible_weapons(state, mod):
        raise ValueError("No hay mejora válida para esta arma")
    state["weapons"][weapon]["mods"] = mod
    return weapon_config(weapon, mod)


def apply_next_upgrade(state, weapon, max_mod=2):
    if weapon not in eligible_next_weapons(state, max_mod):
        raise ValueError("No hay mejora válida para esta arma")
    target = state["weapons"][weapon]["mods"] + 1
    apply_upgrade(state, weapon, target)
    return target
