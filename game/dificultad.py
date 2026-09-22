DIFFICULTIES = {
    "clasico": {
        "label": "CLÁSICO",
        "enemy_count": 3,
        "speed": 0.75,
        "damage": 8,
        "attack_interval": 1.7,
        "resources": 1.0,
        "manual_rate": 0.15,
        "mod": 1,
        "pistol_reserve": 48,
        "shotgun_reserve": 12,
    },
    "doom": {
        "label": "DOOM",
        "enemy_count": 6,
        "speed": 1.12,
        "damage": 14,
        "attack_interval": 1.05,
        "resources": 0.55,
        "manual_rate": 0.55,
        "mod": 2,
        "pistol_reserve": 24,
        "shotgun_reserve": 6,
    },
}


def get_difficulty(key):
    if key not in DIFFICULTIES:
        raise ValueError("Dificultad desconocida")
    return dict(DIFFICULTIES[key])
