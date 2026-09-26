"""Engine contracts, using a synthetic level (never shipped as playable content)."""

import copy
import math
import random
from pathlib import Path
import pytest
from game.engine import GameEngine
from game.nivel import LEVELS, industrial_test, level_config
from game.save_system import load_save, SaveError, SAVE_VERSION, validate_state
from game.world import pickup, advance, initial_progress, solid, clear_line
from game.preguntas import generate_question


def call(e, action, **data):
    r = e.handle(dict(id=str(random.random()), action=action, data=data))
    assert "error" not in r, r
    return r


def reject(e, action, **data):
    r = e.handle(dict(id=str(random.random()), action=action, data=data))
    assert "error" in r
    return r


@pytest.fixture
def lab(monkeypatch):
    l = industrial_test()
    l["id"] = "contract_lab"
    l["grid"] = [[1] * 40] + [[1] + [0] * 38 + [1] for _ in range(18)] + [[1] * 40]
    l["enemy_types"]["worker"]["hp"] = 340
    l["encounters"] = {
        d: [dict(id="sleep", type="worker", x=30.5, y=14.5, group="wave", active=False)]
        for d in ("clasico", "doom")
    }
    l["doors"] = [{"id": "gate_a", "cell": [8, 3]}, {"id": "gate_b", "cell": [12, 3]}]
    for d in l["doors"]:
        l["grid"][d["cell"][1]][d["cell"][0]] = 3

    def st(i, k, x, reward):
        return dict(
            id=i,
            kind=k,
            x=x,
            y=2.5,
            interaction_point={"x": x, "y": 3.5},
            interaction_distance=2,
            question={
                "categories_allowed": ["to_decimal"],
                "denominators_allowed": [2, 4, 8],
                "manual_allowed": True,
                "multiple_choice_allowed": False,
            },
            reward=reward,
        )

    l["stations"] = [
        st("mad_a", "mad", 3.5, [{"type": "upgrade", "mod": 1}]),
        st("mad_b", "mad", 5.5, [{"type": "upgrade", "mod": 1}]),
        st("gate_console_a", "door", 8.5, [{"type": "door", "id": "gate_a"}]),
        st("gate_console_b", "door", 12.5, [{"type": "door", "id": "gate_b"}]),
        st("exit_lab", "exit", 36.5, []),
    ]
    # Embedded terminal visual in a wall, interaction point in the open.
    l["grid"][2][8] = 1
    l["stations"][2]["interaction_point"] = {"x": 7.5, "y": 3.5}
    l["stations"][3]["interaction_point"] = {"x": 11.5, "y": 3.5}
    l["checkpoints"] = [
        dict(
            id="arrival",
            order=0,
            zone=[2, 2, 5, 5],
            prerequisites={},
            respawn_position={"x": 3.5, "y": 4.5},
            respawn_angle=0.5,
        ),
        dict(
            id="safe",
            order=1,
            zone=[32, 2, 36, 5],
            prerequisites={"objective": "fuse_collected"},
            respawn_position={"x": 34.5, "y": 3.5},
            respawn_angle=1.5,
        ),
    ]
    l["items"] = [
        dict(
            id="fuse",
            type="quest_item",
            item_id="main_power_fuse",
            x=4.5,
            y=4.5,
            amount=1,
        ),
        dict(id="sg", type="weapon", weapon="shotgun", x=5.5, y=4.5, amount=1),
        dict(id="key", type="key_item", item_id="storage_key", x=6.5, y=4.5, amount=1),
        dict(
            id="secret_pickup",
            type="secret_item",
            secret_id="logo",
            x=7.5,
            y=4.5,
            amount=1,
        ),
    ]
    l["objectives"] = [
        {"id": "fuse_collected", "condition": {"item": "main_power_fuse"}},
        {"id": "fuse_installed"},
        {"id": "power_restored"},
        {"id": "loader_defeated"},
    ]
    l["waves"] = [
        {
            "id": "wave_one",
            "groups": ["wave"],
            "rewards": [{"type": "ensure_ammo", "minimum": {"pistol": 24}}],
        }
    ]
    l["triggers"] = [
        {
            "id": "wake",
            "condition": {
                "all": [{"objective": "fuse_collected"}, {"zone": [20, 10, 23, 13]}]
            },
            "actions": [{"type": "activate_wave", "id": "wave_one"}],
        }
    ]
    l["secrets"] = [{"id": "logo", "kind": "utcj", "on_shot": True, "x": 6.5, "y": 4.5}]
    l["exit"] = {
        "station": "exit_lab",
        "condition": {
            "all": [{"objective": "power_restored"}, {"objective": "loader_defeated"}]
        },
    }
    monkeypatch.setitem(LEVELS, "contract_lab", l)
    e = GameEngine()
    call(e, "new", level_id="contract_lab", name="Test")
    return e, l


def solve(e, ident, weapon="pistol"):
    st = next(x for x in e.level()["stations"] if x["id"] == ident)
    e.state["player"].update(**st["interaction_point"])
    call(e, "question", station=ident, weapon=weapon)
    return call(e, "answer", question_id=e.question.id, answer=e.question.answer)


def collect(e, ident):
    snap = copy.deepcopy(e.state)
    snap["collected"].append(ident)
    if ident == "sg":
        snap["weapons"]["shotgun"] = {"loaded": 8, "reserve": 12, "mods": 0}
    e.sync(snap)


def test_two_mads_independent(lab):
    e, _ = lab
    collect(e, "sg")
    solve(e, "mad_a")
    assert not e.state["progress"]["stations"]["mad_b"]
    solve(e, "mad_b", "shotgun")
    assert e.state["weapons"]["shotgun"]["mods"] == 1


def test_no_eligible_mad_not_consumed(lab):
    e, _ = lab
    solve(e, "mad_a")
    e.state["player"].update(x=5.5, y=3.5)
    reject(e, "question", station="mad_b")
    assert not e.state["progress"]["stations"]["mad_b"]
    assert e.state["stats"]["correct"] == 1


def test_two_doors_and_embedded_interaction(lab):
    e, _ = lab
    solve(e, "gate_console_a")
    assert e.state["progress"]["doors"] == {"gate_a": True, "gate_b": False}
    solve(e, "gate_console_b")
    assert all(e.state["progress"]["doors"].values())


def test_fuse_and_keys(lab):
    e, _ = lab
    collect(e, "fuse")
    collect(e, "key")
    assert e.state["inventory"]["quest_items"]["main_power_fuse"] == 1
    assert e.state["inventory"]["key_items"]["storage_key"] == 1
    assert e.state["progress"]["objectives"]["fuse_collected"]
    e.sync(copy.deepcopy(e.state))
    assert e.state["inventory"]["quest_items"]["main_power_fuse"] == 1


def test_dormant_telemetry_cannot_damage_or_activate(lab):
    e, _ = lab
    snap = copy.deepcopy(e.state)
    snap["enemies"][0].update(hp=0, active=True)
    e.sync(snap)
    assert e.state["enemies"][0]["hp"] == 340 and not e.state["enemies"][0]["active"]
    assert e.state["stats"]["kills"] == 0


def test_wave_trigger_persists_and_minimum_ammo(lab):
    e, _ = lab
    collect(e, "fuse")
    e.state["player"].update(x=21, y=11)
    e.state["weapons"]["pistol"].update(loaded=0, reserve=0)
    call(e, "sync")
    assert e.state["enemies"][0]["active"]
    assert e.state["progress"]["waves"]["wave_one"]
    assert e.state["progress"]["triggers"]["wake"]
    assert e.state["weapons"]["pistol"]["reserve"] == 24
    state, cp = load_save(e.pack()["save"])
    assert state == e.state
    e.state["weapons"]["pistol"]["reserve"] = 0
    call(e, "sync")
    assert e.state["weapons"]["pistol"]["reserve"] == 0


def test_trigger_by_event(lab):
    e, l = lab
    l["triggers"][0]["condition"] = {"event": "station:gate_console_a"}
    solve(e, "gate_console_a")
    assert e.state["progress"]["triggers"]["wake"]


def test_checkpoint_data_driven_and_resource_floor(lab):
    e, _ = lab
    collect(e, "fuse")
    collect(e, "sg")
    e.state["player"].update(x=34, y=3, hp=4)
    e.state["weapons"]["pistol"].update(loaded=0, reserve=0)
    e.state["weapons"]["shotgun"].update(loaded=0, reserve=0)
    call(e, "checkpoint", checkpoint="safe")
    assert e.state["player"]["hp"] == 4
    call(e, "restart")
    assert e.state["player"]["hp"] == 50
    assert e.state["player"]["angle"] == 1.5
    assert e.state["player"]["x"] == 34.5
    assert e.state["player"]["grace"] > 0
    assert e.state["weapons"]["pistol"]["reserve"] == 12
    assert e.state["weapons"]["shotgun"]["reserve"] == 4


@pytest.mark.parametrize("at_respawn", [False, True])
def test_checkpoint_unsafe(lab, at_respawn):
    e, _ = lab
    collect(e, "fuse")
    e.state["player"].update(x=32.1, y=3)
    enemy = e.state["enemies"][0]
    enemy.update(active=True, x=34.5 if at_respawn else 32.2, y=3.5)
    reject(e, "checkpoint", checkpoint="safe")
    assert e.state["checkpoint"] == "arrival"


def test_combat_block_dormant_and_los(lab):
    e, _ = lab
    enemy = e.state["enemies"][0]
    enemy.update(x=4.5, y=3.5)
    e.state["player"].update(x=3.5, y=3.5)
    call(e, "question", station="mad_a")
    enemy["active"] = True
    assert "AREA NOT SECURE" in reject(e, "question", station="mad_a")["error"]


def test_station_combat_override(lab):
    e, l = lab
    l["stations"][0]["allow_in_combat"] = True
    e.state["enemies"][0].update(active=True, x=4, y=3)
    solve(e, "mad_a")


def test_save_level_id_bounds_and_enemy_hp(lab):
    e, _ = lab
    e.state["player"].update(x=35, y=17)
    save = e.pack()["save"]
    assert save["version"] == SAVE_VERSION and save["level_id"] == "contract_lab"
    assert load_save(save)[0]["enemies"][0]["hp"] == 340


@pytest.mark.parametrize(
    "corruption", ["version", "level", "checkpoint", "revision", "run"]
)
def test_incompatible_saves(lab, corruption):
    e, _ = lab
    save = e.pack()["save"]
    if corruption == "version":
        save["version"] = 1
    elif corruption == "level":
        save["state"]["level_id"] = "missing"
    elif corruption == "checkpoint":
        save["checkpoint_state"]["level_id"] = "industrial_test"
    elif corruption == "revision":
        save["state"]["level_revision"] = 999
    else:
        save["checkpoint_state"]["run_id"] = "different"
    with pytest.raises(SaveError):
        load_save(save)


def test_station_limited_questions():
    for cat in ("to_decimal", "to_fraction", "equivalence", "simplify"):
        for i in range(100):
            q = generate_question(
                "doom",
                99,
                random.Random(i),
                rules={
                    "categories_allowed": [cat],
                    "denominators_allowed": [2, 4, 8],
                    "manual_allowed": False,
                },
            )
            assert q.category == cat and q.mode == "choice" and q.check(q.answer)
            assert "/16" not in q.prompt and "/32" not in q.prompt




def test_fixed_question_pool_respects_exclusions_and_does_not_leak_answers():
    rules={
        "fixed_questions":[
            dict(prompt="Q1",answer="0.5",choices=["0.5","0.25"],category="to_decimal",mode="choice"),
            dict(prompt="Q2",answer="0.25",choices=["0.25","0.5"],category="to_decimal",mode="choice"),
        ],
        "_exclude_prompts":["Q1"],
    }
    q=generate_question(rules=rules,rng=random.Random(0))
    assert q.prompt=="Q2" and q.check("0.25")

def test_fixed_question():
    q = generate_question(
        rules={
            "fixed_question": dict(
                prompt="Convierte 1/2 a decimal", answer="0.5", category="to_decimal"
            )
        }
    )
    assert q.check(".5") and not q.check("1/2")


@pytest.mark.parametrize(
    "category,wrong",
    [
        ("to_decimal", "1/2"),
        ("to_fraction", "0.5"),
        ("to_fraction", "2/4"),
        ("equivalence", "1/2"),
        ("simplify", "2/4"),
    ],
)
def test_manual_format(category, wrong):
    q = generate_question(
        rules={
            "fixed_question": dict(
                prompt="Formato",
                answer="1/2" if category in ("to_fraction", "simplify") else "0.5",
                category=category,
            )
        }
    )
    assert not q.check(wrong)
    assert q.check(q.answer)


def test_atomic_reward_failure_keeps_question_stats_and_station(lab):
    e, l = lab
    e.state["player"].update(x=3.5, y=3.5)
    call(e, "question", station="mad_a")
    qid = e.question.id
    l["stations"][0]["reward"].append(
        {"type": "ammo", "weapon": "not_a_weapon", "amount": 5}
    )
    before = copy.deepcopy(e.state)
    reject(e, "answer", question_id=qid, answer=e.question.answer)
    assert e.state == before and e.question.id == qid
    l["stations"][0]["reward"].pop()
    call(e, "answer", question_id=qid, answer=e.question.answer)


def test_inventory_reward_preflight(lab):
    e, l = lab
    l["stations"][0]["reward"] = [
        {"type": "consume_item", "item_id": "main_power_fuse"},
        {"type": "objective", "id": "fuse_installed"},
    ]
    e.state["player"].update(x=3.5, y=3.5)
    reject(e, "question", station="mad_a")
    collect(e, "fuse")
    solve(e, "mad_a")
    assert e.state["inventory"]["quest_items"]["main_power_fuse"] == 0


def test_unknown_pickup_rejected_before_collection(lab):
    e, l = lab
    l["items"].append(dict(id="bad", type="typo", x=3, y=3, amount=1))
    snap = copy.deepcopy(e.state)
    snap["collected"].append("bad")
    before = copy.deepcopy(e.state)
    reject(e, "sync", snapshot=snap)
    assert e.state == before and "bad" not in e.state["collected"]


def test_utcj_separate_from_kill(lab):
    e, _ = lab
    snap = copy.deepcopy(e.state)
    snap["secret_hits"] = ["logo"]
    e.sync(snap)
    assert e.state["stats"]["kills"] == 0 and e.state["stats"]["secrets"] == 1
    assert e.state["progress"]["utcj_found"] == ["logo"]
    assert load_save(e.pack()["save"])[0]["progress"]["utcj_found"] == ["logo"]


def test_exit_objectives_not_all_kills(lab):
    e, _ = lab
    e.state["player"].update(x=36.5, y=3.5)
    reject(e, "finish")
    e.state["progress"]["objectives"].update(power_restored=True, loader_defeated=True)
    call(e, "finish")
    assert e.state["enemies"][0]["hp"] > 0


def test_missing_station_controlled(lab):
    e, _ = lab
    reject(e, "question", station="does_not_exist")
    solve(e, "mad_a")


def test_missing_session_code():
    assert GameEngine().handle({"id": "x", "action": "sync"})["code"] == "NEED_SESSION"


@pytest.mark.parametrize("difficulty", ["clasico", "doom"])
def test_industrial_reachability_closed_and_prior_gates(difficulty):
    level = level_config(difficulty)
    progress = initial_progress(level)

    def reachable():
        start = level["checkpoints"][0]["respawn_position"]
        seen = {(int(start["x"]), int(start["y"]))}
        todo = list(seen)
        while todo:
            x, y = todo.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and not solid(
                    level, progress, nx + 0.5, ny + 0.5
                ):
                    seen.add((nx, ny))
                    todo.append((nx, ny))
        return seen

    seen = reachable()
    for st in level["stations"]:
        p = st["interaction_point"]
        if st["kind"] != "exit":
            assert (int(p["x"]), int(p["y"])) in seen
    assert (25, 7) not in seen
    progress["doors"]["power_door"] = True
    assert (25, 7) in reachable()


def test_fixed_denominator_outside_station_pool():
    with pytest.raises(ValueError):
        generate_question(
            rules={
                "denominators_allowed": [2, 4, 8],
                "fixed_question": dict(
                    prompt="Convierte 1/16", answer="0.0625", category="to_decimal"
                ),
            }
        )


def test_multi_gate_reachability_in_order(lab):
    e, l = lab
    # Build a narrow corridor with sequential gates; consoles stand before their own gate.
    l["grid"] = [[1] * 40 for _ in range(20)]
    for x in range(1, 39):
        l["grid"][3][x] = 0
    for d in l["doors"]:
        l["grid"][3][d["cell"][0]] = 3
    l["checkpoints"][0]["respawn_position"] = {"x": 3.5, "y": 3.5}
    for st in l["stations"]:
        st["interaction_point"]["y"] = 3.5
    level = e.level()
    progress = initial_progress(level)

    def reach(x):
        return all(
            not solid(level, progress, col + 0.5, 3.5) for col in range(3, int(x) + 1)
        )

    assert reach(7.5) and not reach(11.5) and not reach(36.5)
    progress["doors"]["gate_a"] = True
    assert reach(11.5) and not reach(36.5)
    progress["doors"]["gate_b"] = True
    assert reach(36.5)


def test_fixed_answer_not_exposed_in_config(lab):
    e, l = lab
    l["stations"][0]["question"] = {
        "fixed_question": dict(
            prompt="Convert 1/2", answer="0.5", category="to_decimal"
        )
    }
    client_question=e.pack()["config"]["level"]["stations"][0]["question"]
    assert "fixed_question" not in client_question
    assert "fixed_questions" not in client_question
    solve(e, "mad_a")


def test_simplification_cannot_repeat_prompt():
    import re

    for i in range(100):
        q = generate_question(
            rng=random.Random(i),
            force="simplify",
            rules={"denominators_allowed": [2, 4, 8]},
        )
        original = re.search(r"\d+/\d+", q.prompt)[0]
        assert not q.check(original) and q.check(q.answer)


def test_station_cannot_override_decimal_format_with_fraction():
    with pytest.raises(ValueError):
        generate_question(
            rules={
                "fixed_question": dict(
                    prompt="1/2 a decimal",
                    answer="1/2",
                    category="to_decimal",
                    expected_format="fraction",
                )
            }
        )


@pytest.mark.parametrize(
    "report",
    [
        None,
        "bad",
        {
            "observations": [],
            "incidents": [],
            "measurements": [],
            "project_utcj": "bad",
        },
    ],
)
def test_malformed_report_save_fails_safely(lab, report):
    e, _ = lab
    save = e.pack()["save"]
    save["state"]["report"] = report
    before = copy.deepcopy(e.state)
    reject(e, "load", save=save)
    assert e.state == before


def test_frontend_checkpoint_null_guard_present_and_first_checkpoint_order():
    """Regression guard for a pre-first-checkpoint frontend state.

    Python normally starts industrial_test at its first checkpoint, but the frontend
    must still tolerate null/missing checkpoint values from transient or restored
    states without dereferencing undefined.order.
    """
    level = industrial_test()
    ordered = sorted(level["checkpoints"], key=lambda c: c["order"])
    assert ordered
    current_order = -1  # JS fallback when find(...) has no match
    next_points = [c for c in ordered if c["order"] > current_order]
    assert next_points[0]["id"] == ordered[0]["id"]

    realtime = (
        Path(__file__).resolve().parents[1] / "ui" / "frontend" / "realtime.js"
    ).read_text(encoding="utf-8")
    assert "const currentOrder = current?.order ?? -1;" in realtime
    assert "c.order > currentOrder" in realtime
