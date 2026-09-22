from .enemigos import ENEMIES
from .dificultad import get_difficulty


def level_config(difficulty):
    grid = [[1] * 28 for _ in range(15)]
    for x1, y1, x2, y2 in [
        (1, 1, 7, 7),
        (8, 4, 11, 5),
        (12, 1, 20, 12),
        (21, 7, 21, 7),
        (22, 5, 26, 10),
    ]:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                grid[y][x] = 0
    for x, y in [(15, 5), (15, 6), (18, 9), (18, 10)]:
        grid[y][x] = 2
    grid[7][21] = 3
    cfg = get_difficulty(difficulty)
    positions = [
        ("worker", 16.5, 7.5),
        ("crawler", 18.5, 4.5),
        ("rivet", 19.5, 11.5),
        ("crawler", 13.5, 10.5),
        ("worker", 18.5, 2.5),
        ("rivet", 20.5, 5.5),
    ]
    enemies = [
        dict(id=f"e{i}", type=t, x=x, y=y, hp=ENEMIES[t]["hp"])
        for i, (t, x, y) in enumerate(positions[: cfg["enemy_count"]])
    ]
    items = [
        dict(id=i, type=t, x=x, y=y, amount=max(1, round(n * cfg["resources"])))
        for i, t, x, y, n in [
            ("shotgun", "shotgun", 6.5, 6.5, 1),
            ("a1", "pistol", 7, 3, 16),
            ("a2", "shells", 13.5, 2.5, 8),
            ("a3", "pistol", 17.5, 11.5, 20),
            ("h1", "health", 6.5, 1.5, 25),
            ("h2", "health", 13.5, 11.5, 30),
            ("v1", "armor", 6, 5.5, 35),
            ("s1", "shells", 20, 9, 8),
        ]
    ]
    return dict(
        id="industrial_test",
        name="DDI · SECTOR DE CALIBRACIÓN",
        grid=grid,
        enemies=enemies,
        items=items,
        stations=[
            dict(id="terminal", x=4.5, y=2.5, label="TERMINAL QC"),
            dict(id="mad", x=14, y=2.5, label="M.A.D."),
            dict(id="door", x=21.5, y=7.5, label="ACCESO BLOQUEADO"),
            dict(id="cache", x=19.5, y=1.5, label="SECURE CACHE"),
            dict(id="exit", x=25.5, y=7.5, label="FIN DE TURNO"),
        ],
    )
