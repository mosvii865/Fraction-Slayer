"""Python owns education, progression and transactions; realtime telemetry is single-player trusted."""

from copy import deepcopy
import uuid
import math
import logging
import time
from .dificultad import get_difficulty
from .armas import weapon_config, WEAPONS
from .nivel import level_config
from .estadisticas import new_stats, register_answer, summary
from .preguntas import generate_question
from .mejoras import MODS, eligible_weapons
from .save_system import make_save, load_save, validate_state, SAVE_VERSION
from .world import (
    entity,
    initial_progress,
    pickup,
    rewards,
    advance,
    condition,
    in_zone,
    unsafe,
    clear_line,
    discover_secret,
)


LOGGER = logging.getLogger('fraction_slayer.engine')
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

def _restore_permanent_progress(current, restored, level):
    """Keep campaign acquisitions across checkpoint restart without keeping local combat progress."""
    current_weapons = current.get("weapons", {})
    for weapon, data in current_weapons.items():
        if weapon not in restored["weapons"]:
            restored["weapons"][weapon] = deepcopy(data)
        else:
            restored["weapons"][weapon]["mods"] = max(
                restored["weapons"][weapon].get("mods", 0), data.get("mods", 0)
            )

    # Weapon pickups represent permanent ownership and must not respawn after death.
    permanent_item_ids = {
        item["id"]
        for item in level.get("items", [])
        if item.get("type") == "weapon" and item.get("id") in current.get("collected", [])
    }
    restored["collected"] = list(dict.fromkeys([*restored.get("collected", []), *permanent_item_ids]))

    # M.A.D. upgrades are campaign decisions. Preserve consumption together with the mod.
    permanent_station_ids = {
        st["id"] for st in level.get("stations", []) if st.get("kind") in ("mad", "armory")
    }
    for ident in permanent_station_ids:
        if current.get("progress", {}).get("stations", {}).get(ident):
            restored["progress"]["stations"][ident] = True

    # UTCJ signals are campaign secrets. Re-apply local secret state so the logo cannot be farmed.
    campaign = restored.get("campaign", {})
    current_campaign = current.get("campaign", {})
    found = list(dict.fromkeys([
        *campaign.get("utcj_found", []),
        *current_campaign.get("utcj_found", []),
    ]))
    campaign["utcj_found"] = found
    local_utcj = {s["id"] for s in level.get("secrets", []) if s.get("kind") == "utcj"}
    old_local = set(restored["progress"].get("utcj_found", []))
    for ident in found:
        if ident in local_utcj:
            restored["progress"]["secrets"][ident] = True
            if ident not in restored["progress"]["utcj_found"]:
                restored["progress"]["utcj_found"].append(ident)
            if ident not in restored["report"]["project_utcj"]:
                restored["report"]["project_utcj"].append(ident)
    newly_restored = set(restored["progress"].get("utcj_found", [])) - old_local
    restored["stats"]["secrets"] += len(newly_restored)

    if current.get("weapon") in restored["weapons"]:
        restored["weapon"] = current["weapon"]
    return restored


class GameEngine:
    def __init__(self):
        self.state = None
        self.checkpoint = None
        self.question = None
        self.context = None
        self.processed = {}
        self.question_history = {}
        self._last_sync_log = -30.0

    def level(self):
        return level_config(self.state["difficulty"], self.state["level_id"])

    def config(self):
        level = self.level()
        # Fixed answers are server-only, just like generated answers.
        for station in level["stations"]:
            station.get("question", {}).pop("fixed_question", None)
            station.get("question", {}).pop("fixed_questions", None)
        return dict(
            difficulty=get_difficulty(self.state["difficulty"]),
            level=level,
            enemies=level["enemy_types"],
            weapons={
                w: weapon_config(w, self.state["weapons"].get(w, {}).get("mods", 0))
                for w in WEAPONS
            },
            eligible_weapons=eligible_weapons(self.state),
        )

    def sync(self, snapshot):
        if not snapshot:
            return
        s = deepcopy(self.state)
        level = self.level()
        if any(snapshot.get(k) != s[k] for k in ("level_id", "run_id")):
            raise ValueError("Estado de otra partida o nivel")
        # Grant only known pickups. Client cannot forge station flags or upgrade levels.
        for ident in snapshot["collected"]:
            if ident not in s["collected"]:
                pickup(s, entity(level, "items", ident), level)
                s["collected"].append(ident)
        s["player"] = deepcopy(snapshot["player"])
        s["weapon"] = snapshot["weapon"]
        for w, a in snapshot["weapons"].items():
            if w not in s["weapons"]:
                raise ValueError("Arma no disponible")
            s["weapons"][w].update(loaded=a["loaded"], reserve=a["reserve"])
        enemies = {e["id"]: e for e in snapshot["enemies"]}
        if set(enemies) != {e["id"] for e in s["enemies"]}:
            raise ValueError("Enemigos inválidos")
        for enemy in s["enemies"]:
            if enemy["active"]:
                incoming = enemies[enemy["id"]]
                for key in (
                    "x",
                    "y",
                    "hp",
                    "facing",
                    "ai_state",
                    "last_known",
                    "search_time",
                    "charge_state",
                    "charge_blocked",
                    "stun_time",
                ):
                    enemy[key] = deepcopy(incoming[key])
                if enemy["type"] == "loader":
                    for key in ("phase_time", "attack_index", "cooldown"):
                        enemy[key] = deepcopy(incoming.get(key, 0))
                if enemy["type"] == "foreman":
                    for key in ("boss_mode", "shielded", "shield_cycles", "node_a_hp", "node_b_hp",
                                "phase_time", "attack_index", "cooldown", "support_deployed"):
                        enemy[key] = deepcopy(incoming.get(key, enemy.get(key)))
        for key in ("seconds", "damage", "ammo_used"):
            s["stats"][key] = max(s["stats"][key], snapshot["stats"][key])
        s["stats"]["kills"] = sum(e["hp"] <= 0 for e in s["enemies"])
        for ident in snapshot.get("secret_hits", []):
            secret = entity(level, "secrets", ident)
            if (
                secret.get("on_shot")
                and math.hypot(
                    secret["x"] - s["player"]["x"], secret["y"] - s["player"]["y"]
                )
                <= weapon_config(s["weapon"])["range"]
                and clear_line(level, s, s["player"], secret)
            ):
                discover_secret(s, level, ident)
        self.state = validate_state(advance(s, level))

    def pack(self, **extra):
        return dict(
            state=deepcopy(self.state),
            config=self.config(),
            stats={
                **summary(self.state["stats"]),
                "utcj_found": len(self.state.get("campaign", {}).get("utcj_found", self.state["progress"]["utcj_found"])),
                "utcj_display": (
                    f'{len(self.state.get("campaign", {}).get("utcj_found", self.state["progress"]["utcj_found"]))}/{self.level().get("campaign_secrets", 4)}'
                    if self.state.get("campaign", {}).get("utcj_found", self.state["progress"]["utcj_found"]) else "???"
                ),
            },
            save=make_save(self.state, self.checkpoint),
            **extra
        )

    def handle(self, event):
        eid = event.get("id")
        if not isinstance(eid, str) or len(eid) > 100:
            return {"id": eid, "error": "Evento inválido"}
        if eid in self.processed:
            return self.processed[eid]
        previous = deepcopy((self.state, self.checkpoint, self.question, self.context))
        try:
            result = self._handle(event)
            result["id"] = eid
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            LOGGER.exception('action=%s level_id=%s checkpoint=%s save_version=%s',
                event.get('action'), (self.state or {}).get('level_id'),
                (self.state or {}).get('checkpoint'), SAVE_VERSION)
            self.state, self.checkpoint, self.question, self.context = previous
            result = {
                "id": eid,
                "error": str(exc),
                "code": (
                    "NEED_SESSION"
                    if self.state is None and event.get("action") not in ("new", "load")
                    else "INVALID_ACTION"
                ),
            }
        action=event.get('action')
        now=time.monotonic()
        if result.get('code')=='NEED_SESSION' or (not result.get('error') and action in ('new','load','sync','checkpoint','question','answer','interact','finish') and (action!='sync' or now-self._last_sync_log>=30)):
            LOGGER.info('action=%s level_id=%s checkpoint=%s save_version=%s code=%s',action,
                (self.state or {}).get('level_id'),(self.state or {}).get('checkpoint'),SAVE_VERSION,result.get('code','OK'))
            if action=='sync': self._last_sync_log=now
        self.processed[eid] = result
        if len(self.processed) > 64:
            del self.processed[next(iter(self.processed))]
        return result

    def _handle(self, event):
        action = event["action"]
        data = event.get("data", {})
        if action == "new":
            diff = data.get("difficulty", "clasico")
            cfg = get_difficulty(diff)
            level = level_config(diff, data.get("level_id", "industrial_test"))
            cp = min(level["checkpoints"], key=lambda c: c["order"])
            self.state = dict(
                run_id=uuid.uuid4().hex,
                name=str(data.get("name", "")).strip()[:24] or "Practicante",
                difficulty=diff,
                level_id=level["id"],
                level_revision=level["revision"],
                checkpoint=cp["id"],
                player=dict(
                    **cp["respawn_position"],
                    angle=cp["respawn_angle"],
                    hp=level["player_config"]["max_hp"],
                    armor=0,
                    grace=0
                ),
                weapon="pistol",
                weapons=deepcopy(level.get("initial_loadout", {"pistol": dict(loaded=12, reserve=cfg["pistol_reserve"], mods=0)})),
                enemies=level["enemies"],
                collected=[],
                inventory={"quest_items": {}, "key_items": {}},
                stats=new_stats(),
                progress=initial_progress(level),
                campaign=dict(
                    current_level=level["id"], completed_levels=[], utcj_found=[],
                    global_stats=new_stats(),
                ),
                report=dict(
                    observations=[], incidents=[], measurements=[], project_utcj=[]
                ),
            )
            self.state = validate_state(advance(self.state, level))
            self.checkpoint = deepcopy(self.state)
            self.question = None
            self.context = None
            self.question_history = {}
            return self.pack(kind="start")
        if action == "load":
            self.state, self.checkpoint = load_save(data["save"])
            self.question = None
            self.context = None
            self.question_history = {}
            return self.pack(kind="start")
        if self.state is None:
            raise ValueError("Inicia una partida")
        self.sync(data.get("snapshot"))
        level = self.level()
        self.state = advance(self.state, level)
        if action in ("question", "interact"):
            station = entity(level, "stations", data["station"])
            weapon = data.get("weapon", "pistol")
            p = self.state["player"]
            point = station["interaction_point"]
            direct_interaction = station["kind"] in ("install", "armory")
            if station["kind"] == "exit" or direct_interaction != (action == "interact"):
                raise ValueError("Esta estación no tiene calibración")
            if math.hypot(p["x"] - point["x"], p["y"] - point["y"]) > station[
                "interaction_distance"
            ] or not clear_line(level, self.state, p, point):
                raise ValueError("Acércate a la estación")
            if not station.get("allow_in_combat") and unsafe(level, self.state):
                raise ValueError("AREA NOT SECURE")
            if not condition(station.get("prerequisites", {}), self.state, level):
                raise ValueError("Falta un objetivo previo")
            if self.state["progress"]["stations"][station["id"]]:
                raise ValueError("Estación ya utilizada")
            if station["kind"] == "mad" and weapon not in eligible_weapons(self.state):
                raise ValueError(
                    "No hay arma mejorable. M.A.D. disponible para después."
                )
            if action == "interact":
                candidate = rewards(self.state, level, station["reward"])
                candidate["progress"]["stations"][station["id"]] = True
                self.state = validate_state(advance(candidate, level, event="station:" + station["id"]))
                return self.pack(kind="interaction")
            # Preflight now, and again at commit, without consuming anything.
            rewards(self.state, level, station["reward"], weapon)
            rules = deepcopy(station.get("question") or {})
            if rules.get("fixed_questions"):
                rules["_exclude_prompts"] = list(self.question_history.get(station["id"], set()))
            self.question = generate_question(
                self.state["difficulty"],
                self.state["stats"]["correct"],
                rules=rules,
            )
            self.question_history.setdefault(station["id"], set()).add(self.question.prompt)
            self.context = (station["id"], weapon)
            return dict(
                kind="question", question=self.question.public(), station=station["id"]
            )
        if action == "answer":
            if not self.question or self.question.id != data["question_id"]:
                raise ValueError("Pregunta expirada")
            correct = self.question.check(str(data.get("answer", ""))[:64])
            ident, weapon = self.context
            station = entity(level, "stations", ident)
            candidate = (
                rewards(self.state, level, station["reward"], weapon)
                if correct
                else deepcopy(self.state)
            )
            register_answer(candidate["stats"], correct)
            if correct:
                candidate["progress"]["stations"][ident] = True
                candidate["report"]["measurements"].append(
                    dict(station=ident, correct=True)
                )
            explanation = self.question.explanation
            self.state = validate_state(
                advance(candidate, level, event="station:" + ident if correct else None)
            )
            self.question = None
            self.context = None
            return self.pack(
                kind="answer",
                correct=correct,
                explanation=explanation,
                reward=(
                    MODS.get(weapon, "")
                    if correct and station["kind"] == "mad"
                    else ident
                ),
            )
        if action == "next_level":
            if not self.state["progress"]["complete"]:
                raise ValueError("Completa el nivel antes de continuar")
            next_id = level.get("next_level")
            if not next_id:
                raise ValueError("El siguiente nivel todavía no está disponible")
            next_level = level_config(self.state["difficulty"], next_id)
            cp = min(next_level["checkpoints"], key=lambda c: c["order"])
            carried_weapons = deepcopy(self.state["weapons"])
            resupply = next_level.get("transition_resupply", {})
            for w, minimum in resupply.get("ammo", {}).items():
                if w in carried_weapons:
                    carried_weapons[w]["reserve"] = max(carried_weapons[w]["reserve"], int(minimum))
            campaign = deepcopy(self.state["campaign"])
            campaign["current_level"] = next_id
            hp = max(self.state["player"]["hp"], resupply.get("min_hp", 60))
            hp = min(next_level["player_config"]["max_hp"], hp)
            armor = min(next_level["player_config"]["max_armor"], self.state["player"]["armor"])
            selected = self.state["weapon"] if self.state["weapon"] in carried_weapons else next(iter(carried_weapons))
            self.state = dict(
                run_id=self.state["run_id"], name=self.state["name"], difficulty=self.state["difficulty"],
                level_id=next_id, level_revision=next_level["revision"], checkpoint=cp["id"],
                player=dict(**cp["respawn_position"], angle=cp["respawn_angle"], hp=hp, armor=armor, grace=0),
                weapon=selected, weapons=carried_weapons, enemies=next_level["enemies"], collected=[],
                inventory={"quest_items": {}, "key_items": {}}, stats=new_stats(),
                progress=initial_progress(next_level), campaign=campaign,
                report=dict(observations=[], incidents=[], measurements=[], project_utcj=list(campaign["utcj_found"])),
            )
            self.state = validate_state(advance(self.state, next_level))
            self.checkpoint = deepcopy(self.state)
            self.question = None
            self.context = None
            self.question_history = {}
            return self.pack(kind="transition", transition=dict(from_level=level["id"], to_level=next_id))
        if action == "checkpoint":
            cp = entity(level, "checkpoints", data["checkpoint"])
            current = entity(level, "checkpoints", self.state["checkpoint"])
            if (
                self.state["player"]["hp"] <= 0
                or cp["order"] <= current["order"]
                or not in_zone(self.state["player"], cp["zone"])
                or not condition(cp["prerequisites"], self.state, level)
            ):
                raise ValueError("Checkpoint no disponible")
            if unsafe(level, self.state, checkpoint=True) or unsafe(
                level, self.state, cp["respawn_position"], checkpoint=True
            ):
                raise ValueError("Checkpoint inseguro: AREA NOT SECURE")
            self.state["checkpoint"] = cp["id"]
            self.checkpoint = deepcopy(self.state)
            self.checkpoint["player"].update(
                **cp["respawn_position"], angle=cp["respawn_angle"]
            )
            self.checkpoint = validate_state(self.checkpoint)
            return self.pack(kind="checkpoint")
        if action == "restart":
            current = deepcopy(self.state)
            self.state = _restore_permanent_progress(current, deepcopy(self.checkpoint), level)
            rules = level["respawn_rules"]
            p = self.state["player"]
            p["hp"] = min(
                level["player_config"]["max_hp"], max(p["hp"], rules["min_hp"])
            )
            p["grace"] = rules["grace"]
            self.state = rewards(
                self.state, level, [{"type": "ensure_ammo", "minimum": rules["ammo"]}]
            )
            self.question = None
            self.context = None
            return self.pack(kind="start")
        if action == "finish":
            station = entity(level, "stations", level["exit"]["station"])
            p = self.state["player"]
            point = station["interaction_point"]
            if (
                not condition(level["exit"]["condition"], self.state, level)
                or math.hypot(p["x"] - point["x"], p["y"] - point["y"])
                > station["interaction_distance"]
            ):
                raise ValueError(
                    "Completa los objetivos del nivel y acércate a la salida"
                )
            self.state["progress"]["complete"] = True
            campaign = self.state["campaign"]
            if self.state["level_id"] not in campaign["completed_levels"]:
                campaign["completed_levels"].append(self.state["level_id"])
                totals = campaign["global_stats"]
                for key, value in self.state["stats"].items():
                    if key == "best_streak":
                        totals[key] = max(totals[key], value)
                    elif key == "streak":
                        totals[key] = value
                    else:
                        totals[key] += value
            self.state = validate_state(advance(self.state, level))
            return self.pack(kind="finish")
        if action in ("sync", "pause", "menu"):
            return self.pack(kind=action)
        raise ValueError("Evento desconocido")
