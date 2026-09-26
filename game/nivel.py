"""Level registry: geometry, encounters and progression are data, not engine rules."""

from copy import deepcopy
from .enemigos import ENEMIES
from .dificultad import get_difficulty


def industrial_test():
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

    def enemy(i, t, x, y):
        return dict(id=i, type=t, x=x, y=y, group="arena", active=True)

    classic = [
        enemy("e0", "worker", 16.5, 7.5),
        enemy("e1", "crawler", 18.5, 4.5),
        enemy("e2", "rivet", 19.5, 11.5),
    ]
    doom = [
        enemy("e0", "worker", 16.5, 7.5),
        enemy("e1", "crawler", 18.5, 4.5),
        enemy("e2", "rivet", 19.5, 11.5),
        enemy("e3", "crawler", 13.5, 10.5),
        enemy("e4", "worker", 18.5, 2.5),
        enemy("e5", "rivet", 20.5, 5.5),
    ]
    items = [
        dict(id=i, type=t, x=x, y=y, amount=n, **extra)
        for i, t, x, y, n, extra in [
            ("shotgun", "weapon", 6.5, 6.5, 1, {"weapon": "shotgun"}),
            ("a1", "ammo", 7, 3, 16, {"weapon": "pistol"}),
            ("a2", "ammo", 13.5, 2.5, 8, {"weapon": "shotgun"}),
            ("a3", "ammo", 17.5, 11.5, 20, {"weapon": "pistol"}),
            ("h1", "health", 6.5, 1.5, 25, {}),
            ("h2", "health", 13.5, 11.5, 30, {}),
            ("v1", "armor", 6, 5.5, 35, {}),
            ("s1", "ammo", 20, 9, 8, {"weapon": "shotgun"}),
        ]
    ]

    def station(i, kind, x, y, label, reward, **extra):
        return dict(
            id=i,
            kind=kind,
            x=x,
            y=y,
            label=label,
            interaction_point=dict(x=x, y=y),
            interaction_distance=1.9,
            question={},
            reward=reward,
            **extra,
        )

    stations = [
        station(
            "terminal",
            "terminal",
            4.5,
            2.5,
            "TERMINAL QC",
            [{"type": "ammo", "weapon": "pistol", "amount": 12}],
        ),
        station("mad", "mad", 14, 2.5, "M.A.D.", [{"type": "upgrade", "mod": 1}]),
        station(
            "door",
            "door",
            21.5,
            7.5,
            "ACCESO BLOQUEADO",
            [{"type": "door", "id": "power_door"}],
            door_id="power_door",
        ),
        station(
            "cache",
            "cache",
            19.5,
            1.5,
            "SECURE CACHE",
            [
                {"type": "health", "amount": 35},
                {"type": "ammo", "weapon": "pistol", "amount": 24},
                {"type": "secret", "id": "qc_cache"},
            ],
        ),
        station("exit", "exit", 25.5, 7.5, "FIN DE TURNO", []),
    ]
    stations[2]["interaction_point"] = {"x": 20.5, "y": 7.5}
    return dict(
        id="industrial_test",
        revision=1,
        name="DDI · SECTOR DE CALIBRACIÓN",
        grid=grid,
        enemy_types=deepcopy(ENEMIES),
        encounters={"clasico": classic, "doom": doom},
        items=items,
        stations=stations,
        doors=[{"id": "power_door", "cell": [21, 7]}],
        checkpoints=[
            dict(
                id="inicio",
                order=0,
                zone=[2, 3, 5, 6],
                prerequisites={},
                respawn_position={"x": 3.5, "y": 4.5},
                respawn_angle=0,
            ),
            dict(
                id="arena",
                order=1,
                zone=[10.5, 4, 12, 6],
                prerequisites={},
                respawn_position={"x": 10.7, "y": 4.5},
                respawn_angle=0,
            ),
            dict(
                id="final",
                order=2,
                zone=[18, 1, 21, 13],
                prerequisites={"objective": "arena_cleared"},
                respawn_position={"x": 19.5, "y": 7.5},
                respawn_angle=0,
            ),
        ],
        triggers=[],
        waves=[],
        objectives=[
            {"id": "arena_cleared", "condition": {"group_defeated": "arena"}},
            {"id": "access_open", "condition": {"door_open": "power_door"}},
        ],
        secrets=[{"id": "qc_cache", "kind": "cache"}],
        exit={
            "station": "exit",
            "condition": {
                "all": [{"objective": "arena_cleared"}, {"objective": "access_open"}]
            },
        },
        player_config={"max_hp": 100, "max_armor": 100},
        respawn_rules={
            "min_hp": 50,
            "grace": 2.5,
            "ammo": {"pistol": 12, "shotgun": 4},
        },
    )


from .workshop import workshop
from .factory import factory

LEVELS = {"industrial_test": industrial_test, "workshop": workshop, "factory": factory}


def level_config(difficulty, level_id="industrial_test"):
    cfg = get_difficulty(difficulty)
    if level_id not in LEVELS:
        raise ValueError("Nivel desconocido o incompatible")
    source = LEVELS[level_id]
    level = deepcopy(source() if callable(source) else source)
    grid = level["grid"]
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Grid inválido")
    level.update(width=len(grid[0]), height=len(grid))
    for t in level["enemy_types"].values():
        for k, v in dict(
            radius=0.18,
            vision=11,
            search_seconds=6,
            rear_multiplier=1,
            rear_angle=1.05,
            charge_speed=0,
            stun_seconds=1,
        ).items():
            t.setdefault(k, v)
    level["enemies"] = []
    for entry in level["encounters"][difficulty]:
        enemy = dict(
            hp=level["enemy_types"][entry["type"]]["hp"],
            facing=0,
            ai_state="idle",
            last_known=None,
            search_time=0,
            charge_state="idle",
            charge_blocked=False,
            stun_time=0,
            active=True,
            group="default",
        )
        enemy.update(entry)
        level["enemies"].append(enemy)
    level["items"] = [i for i in level["items"] if difficulty in i.get("difficulties", [difficulty])]
    for item in level["items"]:
        if level.get("scale_resources", True) and item["type"] in ("ammo", "health", "armor"):
            item["amount"] = max(1, round(item["amount"] * cfg["resources"]))
    if difficulty == "doom" and level_id in ("workshop", "factory"):
        for station in level["stations"]:
            # Optional conversion stations become manual in DOOM; theory stays multiple choice.
            q = station.get("question", {})
            fixed = q.get("fixed_question", {})
            if station["kind"] in ("mad", "cache") and fixed.get("category") != "theory":
                q.update(multiple_choice_allowed=False, manual_allowed=True)
                fixed.update(mode="manual", choices=[])
    for key in (
        "stations",
        "doors",
        "checkpoints",
        "triggers",
        "waves",
        "objectives",
        "secrets",
        "items",
        "enemies",
    ):
        ids = [x["id"] for x in level[key]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"IDs duplicados: {key}")
    level.setdefault("conveyors", [])
    level.setdefault("boss_nodes", [])
    return level
