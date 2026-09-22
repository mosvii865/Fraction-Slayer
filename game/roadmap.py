"""Design metadata only. None of this content is unlocked in v0.1."""

FUTURE_LEVELS = [
    "The Workshop",
    "The Factory",
    "The Laboratory",
    "The Foundry",
    "The Converter",
]
PROJECT_UTCJ = {
    "required_marks": 4,
    "eligible_levels": FUTURE_LEVELS[:4],
    "trigger": "shoot_hidden_mark",
    "reward_weapon": "el_toro",
}
EL_TORO = {
    "name": "EL TORO",
    "concept": "Cañón de cabeza mecánica de toro con dos cuernos simétricos",
    "ammo_type": "Bull Core",
    "rarity": "very_rare",
    "damage_profile": "extremely_high",
    "fire_rate_profile": "extremely_slow",
    "fully_upgraded_on_unlock": True,
    "accepts_mad": False,
}
CONVERTER_BOSS = {"shield_unlock_event": "correct_conversion", "implemented": False}
