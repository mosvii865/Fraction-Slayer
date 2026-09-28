"""Campaign metadata through Level 04 — The Foundry."""

CAMPAIGN_LEVELS = [
    "The Workshop",
    "The Factory",
    "The Laboratory",
    "The Foundry",
    "The Converter",
]

IMPLEMENTED_LEVELS = ["The Workshop", "The Factory", "The Laboratory", "The Foundry"]
FUTURE_LEVELS = ["The Converter"]

PROJECT_UTCJ = {
    "required_marks": 4,
    "eligible_levels": CAMPAIGN_LEVELS[:4],
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
