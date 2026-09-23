"""Python owns education, progression and transactions; realtime telemetry is single-player trusted."""

from copy import deepcopy
import uuid
import math
from .dificultad import get_difficulty
from .armas import weapon_config, WEAPONS
from .nivel import level_config
from .estadisticas import new_stats, register_answer, summary
from .preguntas import generate_question
from .mejoras import MODS, eligible_weapons
from .save_system import make_save, load_save, validate_state
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


class GameEngine:
    def __init__(self):
        self.state = None
        self.checkpoint = None
        self.question = None
        self.context = None
        self.processed = {}

    def level(self):
        return level_config(self.state["difficulty"], self.state["level_id"])

    def config(self):
        level = self.level()
        # Fixed answers are server-only, just like generated answers.
        for station in level["stations"]:
            station.get("question", {}).pop("fixed_question", None)
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
                "utcj_found": len(self.state["progress"]["utcj_found"]),
                "utcj_display": len(self.state["progress"]["utcj_found"]) or "???",
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
                weapons={
                    "pistol": dict(loaded=12, reserve=cfg["pistol_reserve"], mods=0)
                },
                enemies=level["enemies"],
                collected=[],
                inventory={"quest_items": {}, "key_items": {}},
                stats=new_stats(),
                progress=initial_progress(level),
                report=dict(
                    observations=[], incidents=[], measurements=[], project_utcj=[]
                ),
            )
            self.state = validate_state(advance(self.state, level))
            self.checkpoint = deepcopy(self.state)
            self.question = None
            self.context = None
            return self.pack(kind="start")
        if action == "load":
            self.state, self.checkpoint = load_save(data["save"])
            self.question = None
            self.context = None
            return self.pack(kind="start")
        if self.state is None:
            raise ValueError("Inicia una partida")
        self.sync(data.get("snapshot"))
        level = self.level()
        self.state = advance(self.state, level)
        if action == "question":
            station = entity(level, "stations", data["station"])
            weapon = data.get("weapon", "pistol")
            p = self.state["player"]
            point = station["interaction_point"]
            if station["kind"] == "exit":
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
            # Preflight now, and again at commit, without consuming anything.
            rewards(self.state, level, station["reward"], weapon)
            self.question = generate_question(
                self.state["difficulty"],
                self.state["stats"]["correct"],
                rules=station.get("question"),
            )
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
        if action == "checkpoint":
            cp = entity(level, "checkpoints", data["checkpoint"])
            current = entity(level, "checkpoints", self.state["checkpoint"])
            if (
                cp["order"] <= current["order"]
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
            self.state = deepcopy(self.checkpoint)
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
            return self.pack(kind="finish")
        if action in ("sync", "pause", "menu"):
            return self.pack(kind=action)
        raise ValueError("Evento desconocido")
