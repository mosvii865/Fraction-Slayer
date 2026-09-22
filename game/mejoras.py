from .armas import weapon_config

MODS = {"pistol": "Precision Barrel", "shotgun": "Tight Choke"}


def apply_upgrade(state, weapon):
    if state["progress"]["mad_used"]:
        raise ValueError("Este M.A.D. ya fue utilizado")
    if weapon not in state["weapons"]:
        raise ValueError("Arma no disponible")
    if state["weapons"][weapon]["mods"] >= 1:
        raise ValueError("MOD II estará disponible en otra versión")
    state["weapons"][weapon]["mods"] += 1
    state["progress"]["mad_used"] = True
    return weapon_config(weapon, state["weapons"][weapon]["mods"])
