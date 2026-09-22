"""Discrete authoritative rules. Realtime physics/combat run in the renderer.
Client telemetry is trusted for this single-player prototype, not ranked play.
"""

from copy import deepcopy
import uuid
from .dificultad import get_difficulty
from .armas import weapon_config, WEAPONS
from .enemigos import ENEMIES
from .nivel import level_config
from .estadisticas import new_stats, register_answer, summary
from .preguntas import generate_question
from .mejoras import apply_upgrade, MODS
from .save_system import make_save, load_save, validate_state


class GameEngine:
    def __init__(self):
        self.state = None
        self.checkpoint = None
        self.question = None
        self.context = None
        self.processed = {}

    def config(self):
        s = self.state
        return dict(
            difficulty=get_difficulty(s["difficulty"]),
            level=level_config(s["difficulty"]),
            enemies=ENEMIES,
            weapons={
                w: weapon_config(w, s["weapons"].get(w, {}).get("mods", 0))
                for w in WEAPONS
            },
        )

    def sync(self, snapshot):
        if not self.state or not snapshot:
            return
        candidate = deepcopy(self.state)
        # Only realtime fields cross this boundary; education/progression stay Python-owned.
        for key in ["player", "enemies", "collected", "weapon"]:
            candidate[key] = deepcopy(snapshot[key])
        for key, weapon in snapshot["weapons"].items():
            if (
                key not in candidate["weapons"]
                and key == "shotgun"
                and "shotgun" in candidate["collected"]
            ):
                candidate["weapons"][key] = dict(
                    loaded=8,
                    reserve=get_difficulty(candidate["difficulty"])["shotgun_reserve"],
                    mods=0,
                )
            if key in candidate["weapons"]:
                candidate["weapons"][key].update(
                    loaded=weapon["loaded"], reserve=weapon["reserve"]
                )
        for key in ["seconds", "damage", "ammo_used"]:
            candidate["stats"][key] = max(
                candidate["stats"][key], snapshot["stats"][key]
            )
        candidate["stats"]["kills"] = sum(e["hp"] <= 0 for e in candidate["enemies"])
        self.state = validate_state(candidate)

    def pack(self, **extra):
        return dict(
            state=deepcopy(self.state),
            config=self.config(),
            stats=summary(self.state["stats"]),
            save=make_save(self.state, self.checkpoint),
            **extra
        )

    def handle(self, event):
        eid = event.get("id")
        if not isinstance(eid, str) or len(eid) > 100:
            return {"id": eid, "error": "Evento inválido"}
        if eid in self.processed:
            return self.processed[eid]
        try:
            result = self._handle(event)
            result["id"] = eid
        except (ValueError, KeyError, TypeError) as exc:
            result = {"id": eid, "error": str(exc)}
        self.processed[eid] = result
        if len(self.processed) > 64:
            del self.processed[next(iter(self.processed))]
        return result

    def _handle(self, e):
        action = e["action"]
        data = e.get("data", {})
        if action == "new":
            name = str(data.get("name", "")).strip()[:24] or "Practicante"
            diff = data.get("difficulty", "clasico")
            cfg = get_difficulty(diff)
            level = level_config(diff)
            self.state = dict(
                run_id=uuid.uuid4().hex,
                name=name,
                difficulty=diff,
                checkpoint="inicio",
                player=dict(x=3.5, y=4.5, angle=0, hp=100, armor=0),
                weapon="pistol",
                weapons={
                    "pistol": dict(loaded=12, reserve=cfg["pistol_reserve"], mods=0)
                },
                enemies=level["enemies"],
                collected=[],
                stats=new_stats(),
                progress=dict(
                    mad_used=False,
                    door_open=False,
                    terminal_used=False,
                    cache_used=False,
                    complete=False,
                ),
                report=dict(
                    observations=[], incidents=[], measurements=[], project_utcj=[]
                ),
            )
            self.checkpoint = deepcopy(self.state)
            self.question = None
            return self.pack(kind="start")
        if action == "load":
            self.state, self.checkpoint = load_save(data["save"])
            self.question = None
            return self.pack(kind="start")
        if not self.state:
            raise ValueError("Inicia una partida")
        self.sync(data.get("snapshot"))
        if action == "question":
            station = data["station"]
            weapon = data.get("weapon", "pistol")
            if station not in ["terminal", "door", "mad", "cache"]:
                raise ValueError("Estación inválida")
            position = next(
                x
                for x in level_config(self.state["difficulty"])["stations"]
                if x["id"] == station
            )
            p = self.state["player"]
            if (p["x"] - position["x"]) ** 2 + (p["y"] - position["y"]) ** 2 > 3.5**2:
                raise ValueError("Acércate a la estación")
            flags = {
                "mad": "mad_used",
                "door": "door_open",
                "terminal": "terminal_used",
                "cache": "cache_used",
            }
            if self.state["progress"][flags[station]]:
                raise ValueError("Estación ya utilizada")
            if station == "mad" and weapon not in self.state["weapons"]:
                raise ValueError("Arma no disponible")
            self.question = generate_question(
                self.state["difficulty"], self.state["stats"]["correct"]
            )
            self.context = (station, weapon)
            return {
                "kind": "question",
                "question": self.question.public(),
                "station": station,
            }
        if action == "answer":
            if not self.question or data["question_id"] != self.question.id:
                raise ValueError("Pregunta expirada")
            correct = self.question.check(str(data.get("answer", ""))[:64])
            register_answer(self.state["stats"], correct)
            station, weapon = self.context
            explanation = self.question.explanation
            self.question = None
            if correct:
                if station == "door":
                    self.state["progress"]["door_open"] = True
                elif station == "mad":
                    apply_upgrade(self.state, weapon)
                elif station == "terminal":
                    self.state["progress"]["terminal_used"] = True
                    self.state["weapons"]["pistol"]["reserve"] += 12
                elif station == "cache":
                    self.state["progress"]["cache_used"] = True
                    self.state["stats"]["secrets"] += 1
                    self.state["player"]["hp"] = min(
                        100, self.state["player"]["hp"] + 35
                    )
                    self.state["weapons"]["pistol"]["reserve"] += 24
                self.state["report"]["measurements"].append(
                    dict(station=station, correct=True)
                )
            return self.pack(
                kind="answer",
                correct=correct,
                explanation=explanation,
                reward=(
                    MODS.get(weapon, "") if correct and station == "mad" else station
                ),
            )
        if action == "checkpoint":
            cp = data.get("checkpoint")
            if cp not in ["arena", "final"]:
                raise ValueError("Checkpoint inválido")
            p = self.state["player"]
            if cp == "arena" and not 10 <= p["x"] <= 14:
                raise ValueError("Fuera del checkpoint")
            if cp == "final" and (
                p["x"] < 18 or any(e["hp"] > 0 for e in self.state["enemies"])
            ):
                raise ValueError("Limpia la arena primero")
            self.state["checkpoint"] = cp
            self.checkpoint = deepcopy(self.state)
            return self.pack(kind="checkpoint")
        if action == "restart":
            self.state = deepcopy(self.checkpoint)
            self.question = None
            return self.pack(kind="start")
        if action == "finish":
            if (
                not self.state["progress"]["door_open"]
                or self.state["player"]["x"] < 24
                or any(e["hp"] > 0 for e in self.state["enemies"])
            ):
                raise ValueError("Elimina a los enemigos y abre el acceso")
            self.state["progress"]["complete"] = True
            return self.pack(kind="finish")
        if action in ["sync", "pause", "menu"]:
            return self.pack(kind=action)
        raise ValueError("Evento desconocido")
