import copy
import pytest

from game.engine import GameEngine
from game.nivel import level_config
from game.world import advance, discover_secret, pickup, rewards
from game.save_system import load_save, SAVE_VERSION


def call(engine, action, **data):
    ident = f"{action}-{len(engine.processed)}"
    result = engine.handle({"id": ident, "action": action, "data": data})
    assert not result.get("error"), result
    return result


def new_factory(diff="clasico"):
    e = GameEngine()
    call(e, "new", name="Factory Test", difficulty=diff, level_id="factory")
    return e


def defeat_group(e, group):
    for enemy in e.state["enemies"]:
        if enemy["group"] == group:
            enemy["hp"] = 0
    e.state = advance(e.state, e.level())


def test_factory_registered_and_counts():
    c = level_config("clasico", "factory")
    d = level_config("doom", "factory")
    assert c["id"] == "factory" and c["name"] == "LEVEL 02 / THE FACTORY"
    assert len(c["enemies"]) == 30
    assert len(d["enemies"]) == 42
    assert {x["type"] for x in c["enemies"]} >= {"worker", "crawler", "rivet", "sentinel", "gunner", "foreman"}
    assert len(c["conveyors"]) == 3
    assert len(c["boss_nodes"]) == 2


def test_factory_weapons_mads_and_math_pool():
    level = level_config("clasico", "factory")
    assert {i.get("weapon") for i in level["items"] if i["type"] == "weapon"} == {"assault", "sawed_off"}
    assert len([s for s in level["stations"] if s["kind"] == "mad"]) == 3
    assert {s["id"] for s in level["secrets"] if s["kind"] == "utcj"} == {"utcj_factory"}
    for st in level["stations"]:
        q = st.get("question", {})
        if q.get("denominators_allowed"):
            assert set(q["denominators_allowed"]) <= {2, 4, 8, 16}


def test_conveyor_zones_are_in_bounds_and_have_walkable_space():
    level = level_config("clasico", "factory")
    for belt in level["conveyors"]:
        x1, y1, x2, y2 = belt["zone"]
        assert 0 <= x1 < x2 < level["width"] and 0 <= y1 < y2 < level["height"]
        cells = [level["grid"][y][x] for y in range(int(y1), int(y2) + 1) for x in range(int(x1), int(x2) + 1)]
        assert 0 in cells
        assert belt["speed"] > 0


def test_factory_rush_is_monotonic_and_not_duplicated():
    e = new_factory()
    level = e.level()
    for item_id in ("assault_rifle", "sawed_off"):
        item = next(i for i in level["items"] if i["id"] == item_id)
        pickup(e.state, item, level)
        e.state["collected"].append(item_id)
    e.state["player"].update(x=29, y=27)
    e.state = advance(e.state, level)
    assert e.state["progress"]["waves"]["rush_1"]
    assert not e.state["progress"]["waves"]["rush_2"]
    defeat_group(e, "rush_1")
    assert e.state["progress"]["waves"]["rush_2"]
    defeat_group(e, "rush_2")
    assert e.state["progress"]["waves"]["rush_3"]
    defeat_group(e, "rush_3")
    assert e.state["progress"]["objectives"]["rush_complete"]
    snapshot = copy.deepcopy(e.state["progress"])
    e.state = advance(e.state, e.level())
    assert e.state["progress"] == snapshot


def test_production_controls_spawn_foreman_and_unlock_lab_after_defeat():
    e = new_factory()
    for group in ("rush_1", "rush_2", "rush_3"):
        for enemy in e.state["enemies"]:
            if enemy["group"] == group:
                enemy["hp"] = 0
    e.state = advance(e.state, e.level())
    e.state["progress"]["objectives"]["rush_complete"] = True

    e.state["player"].update(x=21.5, y=27.5)
    q = call(e, "question", station="production_control_a", weapon="pistol")["question"]
    r = call(e, "answer", question_id=q["id"], answer="11/16")
    assert r["correct"] and e.state["progress"]["objectives"]["production_control_a"]

    e.state["player"].update(x=36.5, y=27.5)
    q = call(e, "question", station="production_control_b", weapon="pistol")["question"]
    r = call(e, "answer", question_id=q["id"], answer=".8125")
    assert r["correct"]
    assert e.state["progress"]["objectives"]["production_controls_disabled"]
    boss = next(x for x in e.state["enemies"] if x["type"] == "foreman")
    assert not boss["active"]  # short checkpoint window before entering the arena core
    e.state["player"].update(x=29, y=27)
    e.state = advance(e.state, e.level())
    boss = next(x for x in e.state["enemies"] if x["type"] == "foreman")
    assert boss["active"] and e.state["progress"]["objectives"]["foreman_spawned"]

    boss["hp"] = 0
    e.state = advance(e.state, e.level())
    assert e.state["progress"]["objectives"]["foreman_defeated"]
    assert e.state["progress"]["objectives"]["lab_transit_unlocked"]


def test_foreman_phase_state_survives_save():
    e = new_factory()
    boss = next(x for x in e.state["enemies"] if x["type"] == "foreman")
    boss.update(active=True, hp=210, boss_mode="protected", shielded=True, shield_cycles=1,
                node_a_hp=31, node_b_hp=55, phase_time=.6, attack_index=3, cooldown=.4)
    save = e.pack()["save"]
    assert save["version"] == SAVE_VERSION
    state, _ = load_save(save)
    restored = next(x for x in state["enemies"] if x["type"] == "foreman")
    assert restored["shielded"] and restored["boss_mode"] == "protected"
    assert restored["node_a_hp"] == 31 and restored["node_b_hp"] == 55


def test_factory_utcj_is_independent_campaign_signal():
    e = new_factory()
    discover_secret(e.state, e.level(), "utcj_factory")
    assert e.state["progress"]["utcj_found"] == ["utcj_factory"]
    assert e.state["campaign"]["utcj_found"] == ["utcj_factory"]
    assert e.pack()["stats"]["utcj_display"] == "1/4"


def test_workshop_to_factory_campaign_transition_preserves_loadout_and_drops_local_items():
    e = GameEngine()
    call(e, "new", name="Campaign", difficulty="clasico", level_id="workshop")
    level = e.level()
    shotgun = next(i for i in level["items"] if i["id"] == "pump_shotgun")
    pickup(e.state, shotgun, level)
    e.state["collected"].append("pump_shotgun")
    e.state = rewards(e.state, level, [{"type": "upgrade", "mod": 1}], "shotgun")
    discover_secret(e.state, level, "utcj_workshop")
    e.state["inventory"]["quest_items"]["main_power_fuse"] = 1
    e.state["player"].update(hp=21, armor=17)
    e.state["weapons"]["pistol"]["reserve"] = 3
    e.state["weapons"]["shotgun"]["reserve"] = 2
    e.state["stats"]["correct"] = 2
    e.state["stats"]["attempted"] = 2

    e.state["progress"]["objectives"]["power_restored"] = True
    defeat_group(e, "loader")
    assert e.state["progress"]["objectives"]["elevator_unlocked"]
    e.state["player"].update(x=18.5, y=25.5)
    call(e, "finish")
    assert "workshop" in e.state["campaign"]["completed_levels"]
    assert e.state["campaign"]["global_stats"]["correct"] == 2

    r = call(e, "next_level")
    assert r["kind"] == "transition"
    assert e.state["level_id"] == "factory" and e.state["checkpoint"] == "factory_receiving"
    assert e.state["player"]["hp"] == 60 and e.state["player"]["armor"] == 17
    assert e.state["weapons"]["shotgun"]["mods"] == 1
    assert e.state["weapons"]["pistol"]["reserve"] >= 24
    assert e.state["weapons"]["shotgun"]["reserve"] >= 10
    assert e.state["campaign"]["utcj_found"] == ["utcj_workshop"]
    assert e.state["inventory"] == {"quest_items": {}, "key_items": {}}
    assert e.state["collected"] == []
    assert e.state["stats"]["attempted"] == 0


def test_new_game_factory_is_clean_and_does_not_grant_future_weapons():
    e = new_factory()
    assert set(e.state["weapons"]) == {"pistol"}
    assert e.state["campaign"]["utcj_found"] == []
    assert e.state["campaign"]["completed_levels"] == []


def test_factory_mad_supports_assault_and_sawed_off():
    e = new_factory()
    level = e.level()
    for item_id in ("assault_rifle", "sawed_off"):
        item = next(i for i in level["items"] if i["id"] == item_id)
        pickup(e.state, item, level)
        e.state["collected"].append(item_id)
    assert {"assault", "sawed_off"} <= set(e.config()["eligible_weapons"])
    e.state["player"].update(x=31.5, y=5.5)
    q = call(e, "question", station="mad_factory_01", weapon="assault")["question"]
    r = call(e, "answer", question_id=q["id"], answer=".4375")
    assert r["correct"] and e.state["weapons"]["assault"]["mods"] == 1


def test_factory_finish_needs_controls_and_foreman_not_all_enemies():
    e = new_factory()
    e.state["progress"]["objectives"].update(
        production_control_a=True, production_control_b=True,
        production_controls_disabled=True, foreman_defeated=True,
        lab_transit_unlocked=True,
    )
    e.state["player"].update(x=49.5, y=28.5)
    # Optional dormant enemies are still alive; exit is objective-driven.
    alive = sum(x["hp"] > 0 for x in e.state["enemies"])
    assert alive > 1
    r = call(e, "finish")
    assert r["state"]["progress"]["complete"]
    assert "factory" in r["state"]["campaign"]["completed_levels"]


def test_emergency_armory_recovers_missing_pump_without_math():
    e = new_factory()
    assert "shotgun" not in e.state["weapons"]
    e.state["player"].update(x=7.0, y=11.5)
    r = call(e, "interact", station="factory_armory")
    assert r["kind"] == "interaction"
    assert "shotgun" in e.state["weapons"]
    assert e.state["weapons"]["shotgun"]["reserve"] >= 2  # ensure-ammo uses loaded+reserve floor
    assert e.state["progress"]["stations"]["factory_armory"]


def test_transition_resupply_preserves_resources_above_floor():
    e = GameEngine()
    call(e, "new", name="Campaign Rich", difficulty="clasico", level_id="workshop")
    level = e.level()
    shotgun = next(i for i in level["items"] if i["id"] == "pump_shotgun")
    pickup(e.state, shotgun, level)
    e.state["collected"].append("pump_shotgun")
    e.state["player"].update(hp=88, armor=73)
    e.state["weapons"]["pistol"]["reserve"] = 77
    e.state["weapons"]["shotgun"]["reserve"] = 31
    e.state["progress"]["objectives"]["power_restored"] = True
    defeat_group(e, "loader")
    e.state["player"].update(x=18.5, y=25.5)
    call(e, "finish")
    call(e, "next_level")
    assert e.state["player"]["hp"] == 88
    assert e.state["player"]["armor"] == 73
    assert e.state["weapons"]["pistol"]["reserve"] == 77
    assert e.state["weapons"]["shotgun"]["reserve"] == 31


def test_utcj_total_persists_across_workshop_factory_transition_and_is_order_independent():
    # Factory can be discovered first in a direct developer start.
    direct = new_factory()
    discover_secret(direct.state, direct.level(), "utcj_factory")
    assert direct.pack()["stats"]["utcj_display"] == "1/4"

    # Campaign path retains Workshop signal and can add Factory afterwards.
    e = GameEngine()
    call(e, "new", name="UTCJ Campaign", difficulty="clasico", level_id="workshop")
    discover_secret(e.state, e.level(), "utcj_workshop")
    e.state["progress"]["objectives"]["power_restored"] = True
    defeat_group(e, "loader")
    e.state["player"].update(x=18.5, y=25.5)
    call(e, "finish")
    call(e, "next_level")
    assert e.pack()["stats"]["utcj_display"] == "1/4"
    discover_secret(e.state, e.level(), "utcj_factory")
    assert set(e.state["campaign"]["utcj_found"]) == {"utcj_workshop", "utcj_factory"}
    assert e.pack()["stats"]["utcj_display"] == "2/4"


def test_factory_campaign_save_roundtrip_keeps_campaign_and_local_progress_separate():
    e = GameEngine()
    call(e, "new", name="Roundtrip", difficulty="clasico", level_id="workshop")
    discover_secret(e.state, e.level(), "utcj_workshop")
    e.state["progress"]["objectives"]["power_restored"] = True
    defeat_group(e, "loader")
    e.state["player"].update(x=18.5, y=25.5)
    call(e, "finish")
    call(e, "next_level")

    # Make real Factory-local progress after the transition.
    level = e.level()
    assault = next(i for i in level["items"] if i["id"] == "assault_rifle")
    pickup(e.state, assault, level)
    e.state["collected"].append("assault_rifle")
    discover_secret(e.state, level, "utcj_factory")
    e.state = advance(e.state, level)

    save = e.pack()["save"]
    state, checkpoint = load_save(save)
    assert state["level_id"] == checkpoint["level_id"] == "factory"
    assert state["campaign"]["current_level"] == "factory"
    assert "workshop" in state["campaign"]["completed_levels"]
    assert set(state["campaign"]["utcj_found"]) == {"utcj_workshop", "utcj_factory"}
    assert "assault" in state["weapons"]
    assert state["inventory"] == {"quest_items": {}, "key_items": {}}
    # Checkpoint is intentionally the start-of-Factory checkpoint until a safe later checkpoint is reached.
    assert checkpoint["checkpoint"] == "factory_receiving"


def test_restart_preserves_campaign_acquisitions_but_restores_local_combat_state():
    e = new_factory()
    level = e.level()
    # Establish a checkpoint snapshot before the permanent acquisitions.
    original_enemy = next(x for x in e.state["enemies"] if x["group"] == "receiving")
    original_hp = original_enemy["hp"]

    assault = next(i for i in level["items"] if i["id"] == "assault_rifle")
    pickup(e.state, assault, level)
    e.state["collected"].append("assault_rifle")
    e.state["weapons"]["assault"]["mods"] = 1
    e.state["progress"]["stations"]["mad_factory_01"] = True
    discover_secret(e.state, level, "utcj_factory")
    original_enemy["hp"] = 0  # local combat progress must roll back

    r = call(e, "restart")
    assert "assault" in r["state"]["weapons"]
    assert r["state"]["weapons"]["assault"]["mods"] == 1
    assert "assault_rifle" in r["state"]["collected"]
    assert r["state"]["progress"]["stations"]["mad_factory_01"] is True
    assert r["state"]["progress"]["secrets"]["utcj_factory"] is True
    assert r["state"]["campaign"]["utcj_found"] == ["utcj_factory"]
    restored_enemy = next(x for x in r["state"]["enemies"] if x["id"] == original_enemy["id"])
    assert restored_enemy["hp"] == original_hp


def test_restart_snapshot_commits_just_collected_weapon_and_utcj_before_rollback():
    e = new_factory()
    snapshot = copy.deepcopy(e.state)
    level = e.level()
    assault = next(i for i in level["items"] if i["id"] == "assault_rifle")
    # Reproduce the frontend's unsynced pickup state.
    pickup(snapshot, assault, level)
    snapshot["collected"].append("assault_rifle")
    snapshot["secret_hits"] = ["utcj_factory"]
    snapshot["player"].update(x=50.5, y=2.5, angle=0)
    # Put the server copy in the same valid location so the shot can be verified by sync.
    e.state["player"].update(x=50.5, y=2.5, angle=0)
    result = e.handle({
        "id": "restart-with-snapshot",
        "action": "restart",
        "data": {"snapshot": snapshot},
    })
    assert not result.get("error"), result
    assert "assault" in result["state"]["weapons"]
    assert "assault_rifle" in result["state"]["collected"]
    assert "utcj_factory" in result["state"]["campaign"]["utcj_found"]


def test_rush_requires_both_factory_weapons_before_starting():
    e = new_factory()
    level = e.level()
    e.state["player"].update(x=29, y=27)
    e.state = advance(e.state, level)
    assert not e.state["progress"]["waves"]["rush_1"]

    assault = next(i for i in level["items"] if i["id"] == "assault_rifle")
    pickup(e.state, assault, level)
    e.state["collected"].append("assault_rifle")
    e.state = advance(e.state, level)
    assert not e.state["progress"]["waves"]["rush_1"]

    sawed = next(i for i in level["items"] if i["id"] == "sawed_off")
    pickup(e.state, sawed, level)
    e.state["collected"].append("sawed_off")
    e.state = advance(e.state, level)
    assert e.state["progress"]["waves"]["rush_1"]


def test_lab_transit_gate_is_closed_until_foreman_and_controls_are_done():
    from game.world import solid

    e = new_factory()
    level = e.level()
    assert solid(level, e.state["progress"], 40.5, 27.5)
    e.state["progress"]["objectives"]["production_controls_disabled"] = True
    e.state["progress"]["objectives"]["foreman_defeated"] = True
    e.state = advance(e.state, level)
    assert e.state["progress"]["objectives"]["lab_transit_unlocked"]
    assert e.state["progress"]["doors"]["lab_transit_gate"]
    assert not solid(level, e.state["progress"], 40.5, 27.5)


def test_foreman_checkpoint_zone_covers_either_last_production_control():
    from game.world import in_zone

    level = level_config("clasico", "factory")
    cp = next(c for c in level["checkpoints"] if c["id"] == "factory_foreman")
    assert in_zone({"x": 21.5, "y": 27.5}, cp["zone"])
    assert in_zone({"x": 36.5, "y": 27.5}, cp["zone"])


def test_factory_secret_mad_is_hidden_from_minimap_data():
    level = level_config("clasico", "factory")
    mad2 = next(s for s in level["stations"] if s["id"] == "mad_factory_02")
    mad1 = next(s for s in level["stations"] if s["id"] == "mad_factory_01")
    assert mad2.get("hidden_on_minimap") is True
    assert not mad1.get("hidden_on_minimap", False)


def test_save_validation_rejects_fake_campaign_utcj_and_levels():
    from game.save_system import SaveError, validate_state

    e = new_factory()
    fake = copy.deepcopy(e.state)
    fake["campaign"]["utcj_found"] = ["fake_signal"]
    with pytest.raises(SaveError):
        validate_state(fake)

    fake = copy.deepcopy(e.state)
    fake["campaign"]["completed_levels"] = ["not_a_real_level"]
    with pytest.raises(SaveError):
        validate_state(fake)


def test_dead_foreman_does_not_trigger_support_wave():
    e = new_factory()
    boss = next(x for x in e.state["enemies"] if x["type"] == "foreman")
    boss.update(active=True, hp=0)
    e.state = advance(e.state, e.level())
    assert not e.state["progress"]["waves"]["foreman_support"]


def test_restart_preserves_used_emergency_armory_to_prevent_repeat_resupply():
    e = new_factory()
    e.state["player"].update(x=7.0, y=11.5)
    r = call(e, "interact", station="factory_armory")
    assert r["state"]["progress"]["stations"]["factory_armory"]
    r = call(e, "restart")
    assert r["state"]["progress"]["stations"]["factory_armory"]
    assert "shotgun" in r["state"]["weapons"]


def test_future_utcj_signal_is_rejected_until_its_level_is_registered():
    from game.save_system import SaveError, validate_state

    e = new_factory()
    fake = copy.deepcopy(e.state)
    fake["campaign"]["utcj_found"] = ["utcj_laboratory"]
    with pytest.raises(SaveError):
        validate_state(fake)
