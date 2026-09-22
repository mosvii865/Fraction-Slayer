"""Server-only answers. 70% conversions, 20% applied theory, 10% special."""

from dataclasses import dataclass, asdict
from fractions import Fraction
import random
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

    def check(self, value):
        if self.category == "theory":
            return str(value).strip().casefold() == self.answer.casefold()
        if self.category == "simplify":
            return str(value).strip() == self.answer
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


def generate_question(difficulty="clasico", completed=0, rng=None, force=None):
    rng = rng or random.Random()
    cfg = get_difficulty(difficulty)
    bucket = rng.random()
    category = force or (
        rng.choice(["to_decimal", "to_fraction", "equivalence", "simplify"])
        if bucket < 0.7
        else "theory" if bucket < 0.9 else "special"
    )
    uid = uuid.uuid4().hex
    if category == "theory":
        prompt, answer, distractors, explanation = rng.choice(THEORY)
        choices = [answer, *distractors]
        rng.shuffle(choices)
        return Question(uid, prompt, answer, choices, "choice", category, explanation)
    maximum = 16 if cfg["mod"] == 2 or completed >= 2 else 8
    denominator = rng.choice([2, 4, 8] + ([16] if maximum == 16 else []))
    numerator = rng.randrange(1, denominator)
    value = Fraction(numerator, denominator)
    fraction = str(value)
    decimal = decimal_text(value)
    mode = "manual" if rng.random() < cfg["manual_rate"] else "choice"
    if category == "to_decimal":
        prompt, answer = f"Convierte {fraction}″ a decimal.", decimal
    elif category == "to_fraction":
        prompt, answer = f"Convierte {decimal}″ a fracción simplificada.", fraction
    elif category == "equivalence":
        prompt, answer = (
            f"¿Qué decimal equivale a {numerator * 2}/{denominator * 2}″?",
            decimal,
        )
    elif category == "simplify":
        prompt, answer = (
            f"Simplifica {value.numerator * 3}/{value.denominator * 3}.",
            fraction,
        )
    else:
        category = "special"
        prompt, answer = f"En {numerator}/{denominator}, ¿cuál es el denominador?", str(
            denominator
        )
    if category in ("to_fraction", "simplify"):
        wrong = [str(value + Fraction(k, 32)) for k in [1, 3, 5]]
    elif category == "special":
        wrong = [str(numerator), str(denominator * 2), str(denominator + 1)]
    else:
        wrong = [decimal_text(value + Fraction(k, 32)) for k in [1, 3, 5]]
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
