import copy
import re
from collections import deque
from pathlib import Path

import pytest

from game.armas import WEAPONS, weapon_config
from game.engine import GameEngine
from game.mejoras import eligible_next_weapons
from game.nivel import level_config
from game.preguntas import generate_question
from game.save_system import load_save, validate_state
from game.world import advance, discover_secret, pickup, solid

IDS = iter(range(20000))


def call(engine, action, **data):
    result = engine.handle({"id": f"foundry-{next(IDS)}", "action": action, "data": data})
    assert not result.get("error"), result
    return result


def reject(engine, action, **data):
    result = engine.handle({"id": f"foundry-{next(IDS)}", "action": action, "data": data})
    assert result.get("error"), result
    return result


def new_foundry(diff="clasico"):
    e = GameEngine()
    call(e, "new", name="Foundry Test", difficulty=diff, level_id="foundry")
    return e


def collect(engine, item_id):
    level = engine.level()
    item = next(i for i in level["items"] if i["id"] == item_id)
    pickup(engine.state, item, level)
    if item_id not in engine.state["collected"]:
        engine.state["collected"].append(item_id)
    engine.state = advance(engine.state, level)
    return item


def flood(level, progress, start):
    start = (int(start[0]), int(start[1]))
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if (nx,ny) in seen or not (0 <= nx < level["width"] and 0 <= ny < level["height"]):
                continue
            if solid(level, progress, nx+.5, ny+.5):
                continue
            seen.add((nx,ny)); queue.append((nx,ny))
    return seen


def test_foundry_registered_content_counts_and_identity():
    classic = level_config("clasico", "foundry")
    doom = level_config("doom", "foundry")
    assert classic["name"] == "LEVEL 04 / THE FOUNDRY"
    assert len(classic["enemies"]) == 41
    assert len(doom["enemies"]) == 54
    assert {"furnace_hound", "forge_brute", "crucible"} <= {e["type"] for e in classic["enemies"]}
    assert {i["weapon"] for i in classic["items"] if i["type"] == "weapon"} == {"lmg", "rocket"}
    assert len([s for s in classic["stations"] if s["kind"] == "mad"]) == 4
    assert classic["heat_zones"] and len(classic["crucible_locks"]) == 5
    assert {s["id"] for s in classic["secrets"] if s["kind"] == "utcj"} == {"utcj_foundry"}


def test_foundry_teaches_64_before_assessment_and_applied_qc_is_plain_spanish():
    level = level_config("clasico", "foundry")
    intro = next(s for s in level["stations"] if s["id"] == "foundry_precision_intro")
    first = intro["question"]["fixed_questions"][0]["prompt"].casefold()
    assert "1/32" in first and "divide" in first and "1/64" in first
    pressure = next(s for s in level["stations"] if s["id"] == "pressure_qc")
    text = " ".join(q["prompt"] for q in pressure["question"]["fixed_questions"]).casefold()
    assert "rango permitido" in text and "pieza" in text
    assert "spec " not in text and "part " not in text and "accept" not in text
    for station in level["stations"]:
        allowed = set(station.get("question", {}).get("denominators_allowed", []))
        if allowed:
            assert allowed <= {2,4,8,16,32,64}


def test_foundry_manual_precision_and_mixed_formats_are_real_manual_input():
    level = level_config("clasico", "foundry")
    manual = next(s for s in level["stations"] if s["id"] == "foundry_manual_calibration")
    qdata = copy.deepcopy(manual["question"]["fixed_questions"][0])
    rules = copy.deepcopy(manual["question"]); rules.pop("fixed_questions"); rules["fixed_question"] = qdata
    q = generate_question("clasico", rules=rules)
    assert q.mode == "manual" and q.check("0.171875") and q.check(".171875")
    mixed = next(s for s in level["stations"] if s["id"] == "foundry_mixed")
    qdata = copy.deepcopy(mixed["question"]["fixed_questions"][1])
    rules = copy.deepcopy(mixed["question"]); rules.pop("fixed_questions"); rules["fixed_question"] = qdata
    q = generate_question("clasico", rules=rules)
    assert q.expected_format == "mixed" and q.check("2 5/8") and not q.check("2.625")


def test_foundry_weapons_and_mod_iii_are_real_campaign_options():
    e = new_foundry()
    collect(e, "lmg_weapon"); collect(e, "rocket_launcher")
    assert e.state["weapons"]["lmg"]["loaded"] == 60
    assert e.state["weapons"]["rocket"]["loaded"] == 1
    e.state["weapons"]["assault"] = {"loaded": 30, "reserve": 40, "mods": 2}
    e.state["weapons"]["lmg"]["mods"] = 2
    assert {"assault", "lmg"} <= set(eligible_next_weapons(e.state, 3))
    assert weapon_config("assault", 3)["damage"] > weapon_config("assault", 2)["damage"]
    assert weapon_config("lmg", 3)["capacity"] == 90
    assert weapon_config("rocket", 2)["blast_radius"] > weapon_config("rocket", 0)["blast_radius"]
    e.state["weapons"]["assault"].update(mods=3, loaded=30)
    assert validate_state(e.state)["weapons"]["assault"]["mods"] == 3


def test_laboratory_to_foundry_transition_preserves_campaign_and_resupplies():
    e = GameEngine(); call(e, "new", name="Campaign", difficulty="clasico", level_id="laboratory")
    level = e.level()
    for wid in ("sniper_rifle",):
        item = next(i for i in level["items"] if i["id"] == wid); pickup(e.state,item,level); e.state["collected"].append(wid)
    discover_secret(e.state, level, "utcj_laboratory")
    e.state["progress"]["objectives"].update(k32_defeated=True, source_trace_complete=True)
    e.state["player"].update(x=63.5,y=34.5,hp=22,armor=17)
    call(e, "finish")
    r=call(e,"next_level")
    assert r["transition"] == {"from_level":"laboratory","to_level":"foundry"}
    assert e.state["level_id"] == "foundry" and e.state["player"]["hp"] == 60
    assert e.state["player"]["armor"] == 17 and "sniper" in e.state["weapons"]
    assert e.state["campaign"]["utcj_found"] == ["utcj_laboratory"]


def test_fourth_utcj_signal_unlocks_el_toro_only_at_four_of_four():
    e = new_foundry()
    e.state["campaign"]["utcj_found"] = ["utcj_workshop","utcj_factory","utcj_laboratory"]
    discover_secret(e.state,e.level(),"utcj_foundry")
    e.state=advance(e.state,e.level())
    assert len(e.state["campaign"]["utcj_found"]) == 4
    assert "el_toro" in e.state["weapons"]
    assert e.state["weapons"]["el_toro"] == {"loaded":1,"reserve":2,"mods":0}
    assert WEAPONS["el_toro"]["max_mods"] == 0
    assert "el_toro" not in eligible_next_weapons(e.state, 3)

    other = new_foundry(); discover_secret(other.state,other.level(),"utcj_foundry"); other.state=advance(other.state,other.level())
    assert len(other.state["campaign"]["utcj_found"]) == 1 and "el_toro" not in other.state["weapons"]


def test_foundry_route_gates_prevent_educational_bypasses():
    e = new_foundry(); level = e.level(); progress = e.state["progress"]
    start = (e.state["player"]["x"], e.state["player"]["y"])

    # Manual 1/64 calibration physically gates Heavy Fabrication.
    reachable = flood(level, progress, start)
    assert (30, 20) not in reachable
    progress["doors"]["fabrication_gate"] = True
    assert (30, 20) in flood(level, progress, start)

    # Pressure/QC lesson physically gates Forge Assembly.
    reachable = flood(level, progress, start)
    assert (66, 34) not in reachable
    progress["doors"]["assembly_gate"] = True
    assert (66, 34) in flood(level, progress, start)

    # The Forge Run gate is the final physical seal before The Crucible.
    reachable = flood(level, progress, start)
    assert (12, 35) not in reachable
    progress["doors"]["crucible_gate"] = True
    assert (12, 35) in flood(level, progress, start)


def test_foundry_all_content_is_reachable_when_route_gates_are_open():
    e = new_foundry(); level = e.level(); progress = e.state["progress"]
    for door_id in progress["doors"]:
        progress["doors"][door_id] = True
    reachable = flood(level, progress, (e.state["player"]["x"], e.state["player"]["y"]))

    for station in level["stations"]:
        point = station["interaction_point"]
        assert (int(point["x"]), int(point["y"])) in reachable, station["id"]
    for collection in ("items", "secrets", "enemies"):
        for entity in level[collection]:
            assert (int(entity["x"]), int(entity["y"])) in reachable, entity["id"]


def test_crucible_phase_state_survives_save_roundtrip():
    e=new_foundry(); boss=next(x for x in e.state["enemies"] if x["type"]=="crucible")
    boss.update(active=True,hp=340,boss_mode="meltdown",phase_time=1.3,cooldown=.4,attack_index=8,
                exposure_cycles=1,lock_a_hp=0,lock_b_hp=0,lock_c_hp=0,emergency_a_hp=120,emergency_b_hp=55)
    state,_=load_save(e.pack()["save"]); b=next(x for x in state["enemies"] if x["type"]=="crucible")
    assert b["boss_mode"]=="meltdown" and b["emergency_b_hp"]==55 and b["exposure_cycles"]==1


def test_foundry_exit_requires_crucible_and_emergency_override():
    e=new_foundry(); e.state["player"].update(x=2.5,y=35.5); reject(e,"finish")
    e.state["progress"]["objectives"]["crucible_defeated"] = True
    e.state["player"].update(x=3.5,y=31.5)
    call(e,"interact",station="core_access_terminal")
    e.state["player"].update(x=2.5,y=35.5)
    result=call(e,"finish")
    assert result["state"]["progress"]["complete"]


def test_foundry_frontend_contract_has_heat_heavy_enemies_crucible_and_8_weapons():
    root=Path(__file__).parents[1]
    foundry=(root/"ui/frontend/foundry.js").read_text(encoding="utf-8")
    realtime=(root/"ui/frontend/realtime.js").read_text(encoding="utf-8")
    controls=(root/"ui/frontend/controls.js").read_text(encoding="utf-8")
    renderer=(root/"ui/frontend/renderer.js").read_text(encoding="utf-8")
    assert "updateHeatCycles" in foundry and "updateFurnaceHound" in foundry and "updateForgeBrute" in foundry
    assert "updateCrucible" in foundry and "MELTDOWN SEQUENCE" in foundry and "CORE EXPOSED" in foundry
    assert "owner==='player'" in realtime and "explodePlayerRocket" in realtime
    assert "Digit8" in controls and "el_toro" in controls
    assert "pressure_lock" in renderer and "furnace_hound" in renderer and "crucible" in renderer


def test_foundry_boss_has_no_math_station_inside_crucible_arena():
    level=level_config("clasico","foundry")
    boss_zone=next(z["zone"] for z in level["zones"] if z["label"]=="THE CRUCIBLE")
    bx1,by1,bx2,by2=boss_zone
    math_stations=[s for s in level["stations"] if s["kind"] in ("terminal","mad") and bx1<=s["x"]<=bx2 and by1<=s["y"]<=by2]
    assert math_stations == []
    assert len(level["crucible_locks"]) == 5
