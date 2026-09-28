import copy
import json
import re
from collections import deque
from pathlib import Path

import pytest

from game.armas import weapon_config
from game.engine import GameEngine
from game.mejoras import eligible_next_weapons
from game.nivel import level_config
from game.preguntas import generate_question
from game.save_system import SAVE_VERSION, load_save, validate_state
from game.world import advance, discover_secret, pickup, rewards, solid


IDS = iter(range(10000))


def call(engine, action, **data):
    ident = f"lab-{next(IDS)}"
    result = engine.handle({"id": ident, "action": action, "data": data})
    assert not result.get("error"), result
    return result


def reject(engine, action, **data):
    ident = f"lab-{next(IDS)}"
    result = engine.handle({"id": ident, "action": action, "data": data})
    assert result.get("error"), result
    return result


def new_lab(diff="clasico"):
    engine = GameEngine()
    call(engine, "new", name="Lab Test", difficulty=diff, level_id="laboratory")
    return engine


def collect(engine, item_id):
    level = engine.level()
    item = next(x for x in level["items"] if x["id"] == item_id)
    pickup(engine.state, item, level)
    if item_id not in engine.state["collected"]:
        engine.state["collected"].append(item_id)
    engine.state = advance(engine.state, level)
    return item


def solve(engine, station_id, weapon="pistol"):
    station = next(x for x in engine.level()["stations"] if x["id"] == station_id)
    engine.state["player"].update(station["interaction_point"])
    question = call(engine, "question", station=station_id, weapon=weapon)["question"]
    answer = engine.question.answer
    result = call(engine, "answer", question_id=question["id"], answer=answer)
    assert result["correct"]
    return result


def flood(level, progress, start):
    start = (int(start[0]), int(start[1]))
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in seen:
                continue
            if not (0 <= nx < level["width"] and 0 <= ny < level["height"]):
                continue
            if solid(level, progress, nx + 0.5, ny + 0.5):
                continue
            seen.add((nx, ny))
            queue.append((nx, ny))
    return seen


def test_laboratory_registered_enemy_counts_and_identity():
    classic = level_config("clasico", "laboratory")
    doom = level_config("doom", "laboratory")
    assert classic["id"] == "laboratory"
    assert classic["name"] == "LEVEL 03 / THE LABORATORY"
    assert len(classic["enemies"]) == 37
    assert len(doom["enemies"]) == 49
    assert {e["type"] for e in classic["enemies"]} >= {
        "worker", "crawler", "rivet", "sentinel", "gunner", "stalker", "k32"
    }
    assert len([s for s in classic["stations"] if s["kind"] == "mad"]) == 3
    assert {s["id"] for s in classic["secrets"] if s["kind"] == "utcj"} == {"utcj_laboratory"}
    assert classic["next_level"] == "foundry"


def test_laboratory_teaches_new_math_before_assessing_it_and_never_uses_64ths():
    level = level_config("clasico", "laboratory")
    precision = next(s for s in level["stations"] if s["id"] == "precision_training")
    mixed = next(s for s in level["stations"] if s["id"] == "mixed_measurement_intro")
    first_precision = precision["question"]["fixed_questions"][0]["prompt"].casefold()
    first_mixed = mixed["question"]["fixed_questions"][0]["prompt"].casefold()
    assert "hasta ahora" in first_precision and "1/16" in first_precision and "1/32" in first_precision
    assert "significa" in first_mixed and "1 pulgada" in first_mixed and "3/8" in first_mixed
    all_text = []
    for station in level["stations"]:
        question = station.get("question", {})
        allowed = set(question.get("denominators_allowed", []))
        if allowed:
            assert allowed <= {2, 4, 8, 16, 32}
        for variant in question.get("fixed_questions", []):
            text = " ".join([
                variant.get("prompt", ""), variant.get("answer", ""),
                " ".join(variant.get("choices", [])), variant.get("explanation", ""),
            ])
            all_text.append(text)
            assert 64 not in {int(x) for x in re.findall(r"/\s*(\d+)", text)}
    joined = " ".join(all_text).casefold()
    assert "spec " not in joined and "part " not in joined and "accept?" not in joined


def test_mixed_number_questions_require_the_correct_output_format():
    level = level_config("clasico", "laboratory")
    node_c = next(s for s in level["stations"] if s["id"] == "containment_node_c")
    rules = copy.deepcopy(node_c["question"])
    variant = copy.deepcopy(rules.pop("fixed_questions")[0])
    rules["fixed_question"] = variant
    question = generate_question("clasico", rules=rules)
    assert question.category == "decimal_to_mixed"
    assert question.expected_format == "mixed"
    assert question.check("1 5/8")
    assert not question.check("1.625")
    assert not question.check("1 10/16")  # Must be reduced.


def test_sniper_pickup_and_config_are_real_campaign_weapon():
    engine = new_lab()
    collect(engine, "sniper_rifle")
    assert "sniper" in engine.state["weapons"]
    assert engine.state["weapons"]["sniper"] == {"loaded": 5, "reserve": 15, "mods": 0}
    base = weapon_config("sniper", 0)
    mod1 = weapon_config("sniper", 1)
    mod2 = weapon_config("sniper", 2)
    assert base["damage"] == 145 and base["capacity"] == 5
    assert mod1["spread"] < base["spread"]
    assert mod2["range"] > mod1["range"]


def test_mod_ii_and_station_specific_mad_options():
    engine = new_lab()
    engine.state["weapons"]["pistol"]["mods"] = 1
    collect(engine, "sniper_rifle")
    engine.state["progress"]["objectives"]["mixed_numbers_learned"] = True
    options = engine.config()["mad_options"]["mad_lab_01"]
    by_weapon = {o["weapon"]: o for o in options}
    assert by_weapon["pistol"]["mod"] == 2
    assert by_weapon["sniper"]["mod"] == 1
    assert "Extended Magazine" in by_weapon["pistol"]["name"]
    assert "Stabilized Scope" in by_weapon["sniper"]["name"]
    assert {"pistol", "sniper"} <= set(eligible_next_weapons(engine.state, 2))

    solve(engine, "mad_lab_01", weapon="pistol")
    assert engine.state["weapons"]["pistol"]["mods"] == 2
    assert weapon_config("pistol", 2)["capacity"] == 18


def test_real_v3_factory_save_loads_under_save_version_4():
    fixture = Path(__file__).with_name("fixture_save_v3_factory.json")
    raw = json.loads(fixture.read_text(encoding="utf-8"))
    assert raw["version"] == 3 and SAVE_VERSION == 4
    state, checkpoint = load_save(raw)
    assert state["level_id"] == checkpoint["level_id"] == "factory"
    assert state["campaign"]["current_level"] == "factory"


def test_factory_to_laboratory_transition_preserves_campaign_and_drops_local_state():
    engine = GameEngine()
    call(engine, "new", name="Campaign", difficulty="clasico", level_id="factory")
    level = engine.level()
    for item_id in ("assault_rifle", "sawed_off"):
        item = next(i for i in level["items"] if i["id"] == item_id)
        pickup(engine.state, item, level)
        engine.state["collected"].append(item_id)
    engine.state = rewards(engine.state, level, [{"type": "upgrade", "mod": 1}], "assault")
    discover_secret(engine.state, level, "utcj_factory")
    engine.state["inventory"]["quest_items"]["temporary_factory_item"] = 1
    engine.state["player"].update(hp=24, armor=19)
    engine.state["weapons"]["pistol"]["reserve"] = 2
    engine.state["weapons"]["assault"]["reserve"] = 3
    engine.state["progress"]["objectives"].update(
        production_control_a=True,
        production_control_b=True,
        production_controls_disabled=True,
        foreman_defeated=True,
        lab_transit_unlocked=True,
    )
    engine.state["player"].update(x=49.5, y=28.5)
    call(engine, "finish")
    transition = call(engine, "next_level")
    assert transition["transition"] == {"from_level": "factory", "to_level": "laboratory"}
    assert engine.state["level_id"] == "laboratory"
    assert engine.state["player"]["hp"] == 60 and engine.state["player"]["armor"] == 19
    assert engine.state["weapons"]["assault"]["mods"] == 1
    assert engine.state["weapons"]["pistol"]["reserve"] >= 24
    assert engine.state["weapons"]["assault"]["reserve"] >= 36
    assert engine.state["campaign"]["utcj_found"] == ["utcj_factory"]
    assert engine.state["inventory"] == {"quest_items": {}, "key_items": {}}
    assert engine.state["collected"] == []
    assert engine.state["progress"]["utcj_found"] == []


def test_containment_sequence_opens_both_vault_approaches():
    engine = new_lab()
    collect(engine, "sniper_rifle")
    # The math terminals are deliberately safe-area interactions: clear each local encounter first.
    for group, station in (("wing_a", "containment_node_a"), ("observation", "mixed_measurement_intro"),
                           ("wing_b", "containment_node_b"), ("core", "containment_node_c")):
        for enemy in engine.state["enemies"]:
            if enemy["group"] == group:
                enemy["hp"] = 0
        engine.state = advance(engine.state, engine.level())
        solve(engine, station)
    objectives = engine.state["progress"]["objectives"]
    assert objectives["containment_a"] and objectives["containment_b"] and objectives["containment_c"]
    assert objectives["containment_stability_100"]
    assert engine.state["progress"]["doors"]["vault_gate"]
    assert engine.state["progress"]["doors"]["vault_gate_archive"]


def test_vault_is_physically_sealed_until_containment_is_100_percent():
    engine = new_lab()
    level = engine.level()
    progress = engine.state["progress"]
    start = (engine.state["player"]["x"], engine.state["player"]["y"])
    assert (31, 18) not in flood(level, progress, start)  # Ballistics sealed by lesson gate.
    progress["doors"]["ballistics_gate"] = True
    reachable = flood(level, progress, start)
    assert (41, 33) in reachable  # Node C/core can be reached.
    assert (55, 30) not in reachable  # Neither vault entrance can be bypassed.
    progress["doors"]["vault_gate"] = True
    progress["doors"]["vault_gate_archive"] = True
    assert (55, 30) in flood(level, progress, start)


def test_k32_spawns_only_after_containment_and_vault_intro_are_cleared():
    engine = new_lab()
    level = engine.level()
    engine.state["progress"]["objectives"].update(
        containment_a=True, containment_b=True, containment_c=True
    )
    engine.state = advance(engine.state, level)
    assert engine.state["progress"]["objectives"]["containment_stability_100"]
    engine.state["player"].update(x=55, y=30)
    engine.state = advance(engine.state, level)
    assert engine.state["progress"]["waves"]["vault_intro"]
    assert not engine.state["progress"]["waves"]["k32"]
    for enemy in engine.state["enemies"]:
        if enemy["group"] == "vault_intro":
            enemy["hp"] = 0
    engine.state = advance(engine.state, level)
    assert engine.state["progress"]["waves"]["k32"]
    boss = next(e for e in engine.state["enemies"] if e["type"] == "k32")
    assert boss["active"] and engine.state["progress"]["objectives"]["k32_spawned"]


def test_k32_realtime_phase_state_survives_save_roundtrip():
    engine = new_lab()
    boss = next(e for e in engine.state["enemies"] if e["type"] == "k32")
    boss.update(active=True, hp=275, boss_mode="overload", overload_cycles=1,
                phase_time=2.3, attack_index=7, cooldown=.4, support_deployed=True)
    state, _ = load_save(engine.pack()["save"])
    restored = next(e for e in state["enemies"] if e["type"] == "k32")
    assert restored["boss_mode"] == "overload"
    assert restored["overload_cycles"] == 1
    assert restored["phase_time"] == 2.3 and restored["attack_index"] == 7
    assert restored["support_deployed"] is True


def test_k32_support_wave_is_monotonic_and_not_triggered_after_death():
    engine = new_lab()
    boss = next(e for e in engine.state["enemies"] if e["type"] == "k32")
    boss.update(active=True, hp=220)
    engine.state = advance(engine.state, engine.level())
    assert engine.state["progress"]["waves"]["k32_support"]
    progress = copy.deepcopy(engine.state["progress"])
    engine.state = advance(engine.state, engine.level())
    assert engine.state["progress"] == progress

    other = new_lab()
    dead = next(e for e in other.state["enemies"] if e["type"] == "k32")
    dead.update(active=True, hp=0)
    other.state = advance(other.state, other.level())
    assert not other.state["progress"]["waves"]["k32_support"]


def test_laboratory_utcj_is_independent_and_can_be_third_campaign_signal():
    engine = new_lab()
    discover_secret(engine.state, engine.level(), "utcj_laboratory")
    assert engine.state["campaign"]["utcj_found"] == ["utcj_laboratory"]
    assert engine.pack()["stats"]["utcj_display"] == "1/4"
    engine.state["campaign"]["utcj_found"] = ["utcj_workshop", "utcj_factory", "utcj_laboratory"]
    validate_state(engine.state)
    assert len(engine.state["campaign"]["utcj_found"]) == 3


def test_source_trace_is_required_for_exit_and_core_terminal_is_post_boss():
    engine = new_lab()
    engine.state["player"].update(x=63.5, y=34.5)
    reject(engine, "finish")
    engine.state["progress"]["objectives"]["k32_defeated"] = True
    engine.state["player"].update(x=62.5, y=26.5)
    call(engine, "interact", station="core_analysis_terminal")
    assert engine.state["progress"]["objectives"]["source_trace_complete"]
    engine.state["player"].update(x=63.5, y=34.5)
    result = call(engine, "finish")
    assert result["state"]["progress"]["complete"]


def test_save_validation_accepts_mod_ii_capacity_and_rejects_excess_loaded():
    engine = new_lab()
    engine.state["weapons"]["pistol"].update(mods=2, loaded=18)
    assert validate_state(engine.state)["weapons"]["pistol"]["loaded"] == 18
    bad = copy.deepcopy(engine.state)
    bad["weapons"]["pistol"]["loaded"] = 19
    with pytest.raises(ValueError):
        validate_state(bad)


def test_checkpoint_restart_preserves_mod_ii_mad_and_utcj_campaign_progress():
    engine = new_lab()
    engine.state["weapons"]["pistol"]["mods"] = 1
    engine.state["progress"]["objectives"]["mixed_numbers_learned"] = True
    solve(engine, "mad_lab_01", weapon="pistol")
    discover_secret(engine.state, engine.level(), "utcj_laboratory")
    assert engine.state["weapons"]["pistol"]["mods"] == 2
    assert engine.state["progress"]["stations"]["mad_lab_01"]
    engine.state["player"]["hp"] = 0
    call(engine, "restart")
    assert engine.state["weapons"]["pistol"]["mods"] == 2
    assert engine.state["progress"]["stations"]["mad_lab_01"]
    assert engine.state["progress"]["secrets"]["utcj_laboratory"]
    assert engine.state["progress"]["utcj_found"] == ["utcj_laboratory"]
    assert engine.state["campaign"]["utcj_found"] == ["utcj_laboratory"]


def test_laboratory_frontend_contract_has_mixed_input_k32_and_75_percent_feedback():
    root = Path(__file__).parents[1]
    controls = (root / "ui/frontend/controls.js").read_text(encoding="utf-8")
    game = (root / "ui/frontend/game.js").read_text(encoding="utf-8")
    laboratory = (root / "ui/frontend/laboratory.js").read_text(encoding="utf-8")
    loader = (root / "ui/frontend/loader.js").read_text(encoding="utf-8")
    assert "Digit5" in controls and "sniper" in controls
    assert "␠" in game and "decimal_to_mixed" not in game  # keypad is generic, not hardcoded to one lesson.
    assert "updateStalker" in laboratory and "updateK32" in laboratory
    assert "SOBRECARGA DIMENSIONAL" in laboratory and "¡AHORA!" in laboratory
    assert "ENCRYPTED PAYLOAD: 75%" in loader


def test_optional_archives_terminal_and_core_analysis_have_narrative_panels():
    level = level_config("clasico", "laboratory")
    archive = next(s for s in level["stations"] if s["id"] == "research_archive_terminal")
    core = next(s for s in level["stations"] if s["id"] == "core_analysis_terminal")
    assert "RECONSTRUCCIÓN ORGÁNICA" in " ".join(archive["interaction_panel"]["lines"])
    assert "NO AUTORIZADA" in " ".join(archive["interaction_panel"]["lines"])
    assert any("FOUNDRY" in line for line in core["interaction_panel"]["lines"])
    assert core["prerequisites"] == {"objective": "k32_defeated"}
