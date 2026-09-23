"""Server-only answers. 70% conversions, 20% applied theory, 10% special."""

from dataclasses import dataclass, asdict
from fractions import Fraction
import random
import re
import math
import uuid
from .conversiones import equivalent, decimal_text
from .dificultad import get_difficulty


@dataclass
class Question:
    id: str
    prompt: str
    answer: str
    choices: list[str]
    mode: str
    category: str
    explanation: str

    def public(self):
        data = asdict(self)
        del data["answer"]
        del data["explanation"]
        return data

    expected_format: str = ""
    require_reduced: bool = True

    def __post_init__(self):
        formats = {
            "to_decimal": "decimal",
            "to_fraction": "fraction",
            "simplify": "fraction",
            "special": "integer",
            "theory": "text",
        }
        if self.category not in {*formats, "equivalence"} or self.mode not in (
            "manual",
            "choice",
        ):
            raise ValueError("Categoría o modo de pregunta inválido")
        required = formats.get(self.category)
        if required and self.expected_format and self.expected_format != required:
            raise ValueError("Formato incompatible con la conversión")
        self.expected_format = self.expected_format or required or "decimal"
        if self.expected_format not in ("decimal", "fraction", "integer", "text"):
            raise ValueError("Formato de respuesta inválido")

    def check(self, value):
        value = str(value).strip().replace(",", ".")
        fmt = self.expected_format or (
            {
                "to_decimal": "decimal",
                "equivalence": "decimal",
                "to_fraction": "fraction",
                "simplify": "fraction",
                "special": "integer",
            }.get(self.category, "text")
        )
        if fmt == "text":
            return value.casefold() == self.answer.casefold()
        if fmt == "decimal" and not re.fullmatch(
            r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)", value
        ):
            return False
        if fmt == "integer" and not re.fullmatch(r"[+-]?\d+", value):
            return False
        if fmt == "fraction":
            match = re.fullmatch(r"([+-]?\d+)\s*/\s*([1-9]\d*)", value)
            if not match:
                return False
            if self.require_reduced and math.gcd(int(match[1]), int(match[2])) != 1:
                return False
        return equivalent(value, self.answer)


THEORY = [
    (
        "¿Qué herramienta mide con mayor precisión el diámetro de un eje?",
        "Micrómetro",
        ["Regla escolar", "Cinta métrica", "Transportador"],
        "El micrómetro mide dimensiones pequeñas con alta precisión.",
    ),
    (
        "Una pieza debe medir 0.500 ± 0.005 pulgadas. ¿Cuál medida es aceptable?",
        "0.503",
        ["0.510", "0.490", "0.506"],
        "El intervalo aceptado va de 0.495 a 0.505 pulgadas, incluidos sus extremos.",
    ),
    (
        "Antes de inspeccionar un lote, debes comprobar…",
        "La calibración del instrumento",
        ["El color del empaque", "La marca del uniforme", "La velocidad de la banda"],
        "La calibración permite confiar en la medición.",
    ),
]


def generate_question(
    difficulty="clasico", completed=0, rng=None, force=None, rules=None
):
    rng = rng or random.Random()
    rules = rules or {}
    difficulty = rules.get("difficulty_override", difficulty)
    cfg = get_difficulty(difficulty)
    if rules.get("fixed_question"):
        fixed = dict(rules["fixed_question"])
        fixed.setdefault("choices", [])
        fixed.setdefault("mode", "manual")
        fixed.setdefault("explanation", "Calibración completada.")
        q = Question(id=uuid.uuid4().hex, **fixed)
        if q.mode == "choice" and (
            len(q.choices) < 2
            or len(set(q.choices)) != len(q.choices)
            or sum(q.check(c) for c in q.choices) != 1
        ):
            raise ValueError("Opciones de pregunta fija inválidas")
        if not q.check(q.answer):
            raise ValueError("Formato de pregunta fija inválido")
        if (
            not rules.get("manual_allowed", True)
            and q.mode == "manual"
            or not rules.get("multiple_choice_allowed", True)
            and q.mode == "choice"
        ):
            raise ValueError("Formato deshabilitado")
        if (
            rules.get("categories_allowed")
            and q.category not in rules["categories_allowed"]
        ):
            raise ValueError("Categoría no permitida")
        if rules.get("denominators_allowed"):
            for denominator in re.findall(
                r"/\s*(\d+)", q.prompt + " " + q.answer + " " + " ".join(q.choices)
            ):
                if int(denominator) not in rules["denominators_allowed"]:
                    raise ValueError("Denominador fijo fuera del pool")
        if q.mode == "manual" and q.category == "theory":
            raise ValueError("La teoría requiere opción múltiple en esta versión")
        return q
    if not rules.get("manual_allowed", True) and not rules.get(
        "multiple_choice_allowed", True
    ):
        raise ValueError("No hay formato de pregunta habilitado")
    bucket = rng.random()
    category = force or (
        rng.choice(["to_decimal", "to_fraction", "equivalence", "simplify"])
        if bucket < 0.7
        else "theory" if bucket < 0.9 else "special"
    )
    allowed = rules.get("categories_allowed")
    if allowed is not None:
        if not allowed or set(allowed) - {
            "to_decimal",
            "to_fraction",
            "equivalence",
            "simplify",
            "theory",
            "special",
        }:
            raise ValueError("Categorías inválidas")
        category = force if force in allowed else rng.choice(allowed)
    if not rules.get("multiple_choice_allowed", True) and category == "theory":
        candidates = [
            c
            for c in (
                allowed
                or ["to_decimal", "to_fraction", "equivalence", "simplify", "special"]
            )
            if c != "theory"
        ]
        if not candidates:
            raise ValueError("La teoría requiere opción múltiple en esta versión")
        category = rng.choice(candidates)
    uid = uuid.uuid4().hex
    if category == "theory":
        prompt, answer, distractors, explanation = rng.choice(THEORY)
        choices = [answer, *distractors]
        rng.shuffle(choices)
        return Question(
            uid,
            prompt,
            answer,
            choices if rules.get("multiple_choice_allowed", True) else [],
            "choice" if rules.get("multiple_choice_allowed", True) else "manual",
            category,
            explanation,
        )
    maximum = 16 if cfg["mod"] == 2 or completed >= 2 else 8
    denominators = rules.get(
        "denominators_allowed", [2, 4, 8] + ([16] if maximum == 16 else [])
    )
    if not denominators or any(
        type(d) is not int or d < 2 or d > 64 or d & (d - 1) for d in denominators
    ):
        raise ValueError("Denominadores inválidos")
    denominator = rng.choice(denominators)
    if category == "simplify":
        reducible = [d for d in denominators if d >= 4]
        if not reducible:
            raise ValueError(
                "El pool de simplificación necesita un denominador de al menos 4"
            )
        denominator = rng.choice(reducible)
        numerator = 2 * rng.randrange(1, denominator // 2)
    else:
        numerator = rng.randrange(1, denominator)
    value = Fraction(numerator, denominator)
    fraction = str(value)
    decimal = decimal_text(value)
    mode = "manual" if rng.random() < cfg["manual_rate"] else "choice"
    if not rules.get("manual_allowed", True):
        mode = "choice"
    if not rules.get("multiple_choice_allowed", True):
        mode = "manual"
    if category == "to_decimal":
        prompt, answer = f"Convierte {fraction}″ a decimal.", decimal
    elif category == "to_fraction":
        prompt, answer = f"Convierte {decimal}″ a fracción simplificada.", fraction
    elif category == "equivalence":
        prompt, answer = (
            f"¿Qué decimal equivale a {numerator}/{denominator}″?",
            decimal,
        )
    elif category == "simplify":
        prompt, answer = (
            f"Simplifica {numerator}/{denominator}.",
            fraction,
        )
    else:
        category = "special"
        prompt, answer = f"En {numerator}/{denominator}, ¿cuál es el denominador?", str(
            denominator
        )
    if category in ("to_fraction", "simplify"):
        wrong = [str(value + Fraction(k, max(denominators))) for k in [1, 3, 5]]
    elif category == "special":
        wrong = [str(numerator), str(denominator * 2), str(denominator + 1)]
    else:
        wrong = [
            decimal_text(value + Fraction(k, max(denominators))) for k in [1, 3, 5]
        ]
    choices = [answer, *wrong]
    rng.shuffle(choices)
    explanation = (
        f"El denominador es el número inferior: {denominator}."
        if category == "special"
        else f"{fraction}″ = {decimal}″. Divide el numerador entre el denominador; para simplificar, divide ambos por su máximo común divisor."
    )
    return Question(
        uid,
        prompt,
        answer,
        choices if mode == "choice" else [],
        mode,
        category,
        explanation,
    )
