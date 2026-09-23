import copy
import json
import random
from fractions import Fraction
import pytest
from game.conversiones import parse_number, equivalent, decimal_text
from game.preguntas import generate_question
from game.engine import GameEngine
from game.save_system import load_save, SaveError
from game.dificultad import get_difficulty
from game.nivel import level_config
from game.estadisticas import new_stats, register_answer, accuracy
from game.puntuacion import score


@pytest.mark.parametrize(
    "text,expected",
    [
        ("0.125", Fraction(1, 8)),
        ("0,5", Fraction(1, 2)),
        ("2/4", Fraction(1, 2)),
        ("1 3/16", Fraction(19, 16)),
        ("-1 1/2", Fraction(-3, 2)),
        (' 11/16" ', Fraction(11, 16)),
        (".5", Fraction(1, 2)),
        ("0", Fraction(0)),
    ],
)
def test_parse(text, expected):
    assert parse_number(text) == expected


@pytest.mark.parametrize(
    "text", ["1/0", "1//2", "NaN", "inf", '__import__("os")', "1e1000", "", "9" * 40]
)
def test_bad_numbers(text):
    with pytest.raises(ValueError):
        parse_number(text)


def test_exact_math():
    assert equivalent("0.6875", "11/16")
    assert not equivalent("0.6874", "11/16")
    assert decimal_text(Fraction(11, 16)) == "0.6875"
    assert decimal_text(Fraction(0)) == "0"
    with pytest.raises(ValueError):
        decimal_text(Fraction(1, 3))


@pytest.mark.parametrize("diff", ["clasico", "doom"])
def test_question_bank(diff):
    rng = random.Random(9)
    manual = 0
    for category in [
        "to_decimal",
        "to_fraction",
        "simplify",
        "equivalence",
        "theory",
        "special",
    ]:
        for _ in range(80):
            q = generate_question(diff, 3, rng, force=category)
            assert q.check(q.answer)
            assert not q.check("respuesta incorrecta")
            assert "answer" not in q.public() and "explanation" not in q.public()
            if q.mode == "choice":
                assert len(set(q.choices)) == 4
                assert sum(q.check(c) for c in q.choices) == 1
            else:
                manual += 1
    assert manual > 0


def test_proportions_and_modes():
    counts = {}
    manual = {}
    for diff in ["clasico", "doom"]:
        rng = random.Random(8)
        qs = [generate_question(diff, rng=rng) for _ in range(3000)]
        manual[diff] = sum(q.mode == "manual" for q in qs)
        counts[diff] = sum(
            q.category in ["to_decimal", "to_fraction", "equivalence", "simplify"]
            for q in qs
        ) / len(qs)
    assert all(0.65 < x < 0.75 for x in counts.values())
    assert manual["doom"] > manual["clasico"] * 2


def call(engine, action, **data):
    result = engine.handle(dict(id=str(random.random()), action=action, data=data))
    assert "error" not in result, result
    return result


def new(diff="clasico"):
    e = GameEngine()
    call(e, "new", name="Esteban", difficulty=diff)
    return e


def at(e, station):
    p = next(
        s for s in level_config(e.state["difficulty"])["stations"] if s["id"] == station
    )
    e.state["player"].update(**p["interaction_point"])
    for enemy in e.state["enemies"]:
        enemy["active"] = False


def solve(e, station, weapon="pistol", correct=True):
    at(e, station)
    r = call(e, "question", station=station, weapon=weapon)
    return call(
        e,
        "answer",
        question_id=r["question"]["id"],
        answer=e.question.answer if correct else "incorrecto",
    )


def test_difficulties_differ_beyond_hp():
    a, b = [get_difficulty(k) for k in ["clasico", "doom"]]
    assert (
        b["enemy_count"] > a["enemy_count"]
        and b["damage"] > a["damage"]
        and b["speed"] > a["speed"]
    )
    assert (
        b["resources"] < a["resources"] and b["attack_interval"] < a["attack_interval"]
    )


def test_door_retry_and_replay():
    e = new()
    r = solve(e, "door", correct=False)
    assert (
        not e.state["progress"]["doors"]["power_door"] and r["stats"]["attempted"] == 1
    )
    solve(e, "door")
    assert e.state["progress"]["doors"]["power_door"]
    assert e.state["stats"]["correct"] == 1 and e.state["stats"]["attempted"] == 2
    old = copy.deepcopy(e.state)
    assert "error" in e.handle(
        dict(
            id="stale", action="answer", data={"question_id": "stale", "answer": "0.5"}
        )
    )
    assert e.state == old


@pytest.mark.parametrize("weapon", ["pistol", "shotgun"])
def test_mad_upgrade_once(weapon):
    e = new()
    if weapon == "shotgun":
        snap = copy.deepcopy(e.state)
        snap["collected"].append("shotgun")
        snap["weapons"]["shotgun"] = {"loaded": 8, "reserve": 12, "mods": 0}
        snap["weapon"] = "shotgun"
        e.sync(snap)
    original = e.config()["weapons"][weapon]
    r = solve(e, "mad", weapon)
    assert (
        e.state["weapons"][weapon]["mods"] == 1
        and e.state["progress"]["stations"]["mad"]
    )
    assert r["config"]["weapons"][weapon]["max_mods"] == 4
    if weapon == "pistol":
        assert r["config"]["weapons"][weapon]["damage"] == pytest.approx(
            original["damage"] * 1.15
        )
    else:
        assert (
            r["config"]["weapons"][weapon]["range"] > original["range"]
            and r["config"]["weapons"][weapon]["spread"] < original["spread"]
        )
    assert "error" in e.handle(
        {
            "id": "second",
            "action": "question",
            "data": {"station": "mad", "weapon": weapon},
        }
    )


def test_duplicate_event_does_not_award_twice():
    e = new()
    at(e, "terminal")
    call(e, "question", station="terminal")
    event = {
        "id": "same",
        "action": "answer",
        "data": {"question_id": e.question.id, "answer": e.question.answer},
    }
    first = e.handle(event)
    second = e.handle(event)
    assert first == second and e.state["stats"]["correct"] == 1


def test_client_cannot_overwrite_education_or_upgrade():
    e = new()
    snap = copy.deepcopy(e.state)
    snap["stats"]["correct"] = 999
    snap["progress"]["doors"]["power_door"] = True
    snap["weapons"]["pistol"]["mods"] = 1
    e.sync(snap)
    assert (
        not e.state["progress"]["doors"]["power_door"]
        and e.state["stats"]["correct"] == 0
        and e.state["weapons"]["pistol"]["mods"] == 0
    )


def test_checkpoint_restore_and_save_roundtrip():
    e = new("doom")
    solve(e, "terminal")
    e.state["player"].update(x=11, y=4.5)
    call(e, "checkpoint", checkpoint="arena")
    saved = e.pack()["save"]
    other = GameEngine()
    call(other, "load", save=json.loads(json.dumps(saved)))
    assert e.state == other.state and e.checkpoint == other.checkpoint
    e.state["player"]["hp"] = 0
    e.state["weapons"]["pistol"]["loaded"] = 0
    call(e, "restart")
    assert e.state["player"]["hp"] == 100 and e.state["player"]["grace"] > 0
    assert e.state["checkpoint"] == e.checkpoint["checkpoint"]


@pytest.mark.parametrize(
    "corruption", ["version", "nan", "wall", "negative", "enemies", "name", "stats"]
)
def test_corrupt_save(corruption):
    data = new().pack()["save"]
    if corruption == "version":
        data["version"] = 999
    if corruption == "nan":
        data["state"]["player"]["hp"] = float("nan")
    if corruption == "wall":
        data["state"]["player"].update(x=9, y=2)
    if corruption == "negative":
        data["state"]["weapons"]["pistol"]["reserve"] = -1
    if corruption == "enemies":
        data["state"]["enemies"] = []
    if corruption == "name":
        data["state"]["name"] = ""
    if corruption == "stats":
        data["state"]["stats"]["correct"] = 99
    with pytest.raises(SaveError):
        load_save(data)


def test_finish_requires_door_and_clear_arena():
    e = new()
    assert "error" in e.handle(dict(id="blocked", action="finish"))
    solve(e, "door")
    e.state["player"].update(x=25, y=7.5)
    assert "error" in e.handle(dict(id="blocked2", action="finish"))
    for enemy in e.state["enemies"]:
        enemy["hp"] = 0
    r = call(e, "finish")
    assert r["state"]["progress"]["complete"]


def test_score_accuracy_streak():
    s = new_stats()
    for correct in [True, True, False, True]:
        register_answer(s, correct)
    assert accuracy(s) == 75 and s["best_streak"] == 2 and s["streak"] == 1
    assert score(s) == 705


def test_map_reachability():
    level = level_config("doom")
    g = level["grid"]
    visited = {(3, 4)}
    todo = [(3, 4)]
    while todo:
        x, y = todo.pop()
        for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if (
                0 <= ny < len(g)
                and 0 <= nx < len(g[0])
                and g[ny][nx] in [0, 3]
                and (nx, ny) not in visited
            ):
                visited.add((nx, ny))
                todo.append((nx, ny))
    assert all(
        (int(i["x"]), int(i["y"])) in visited
        for i in level["items"] + level["stations"] + level["enemies"]
    )
