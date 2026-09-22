"""Exact input parsing. No eval, floating-point equality or implicit rounding."""

import re
from fractions import Fraction


def parse_number(value: str) -> Fraction:
    text = str(value).strip().replace(",", ".").removesuffix('"').strip()
    if len(text) > 32:
        raise ValueError("Respuesta demasiado larga")
    if re.fullmatch(r"[+-]?\d+\s+\d+/\d+", text):
        whole, part = text.split()
        result = abs(Fraction(whole)) + Fraction(part)
        return -result if whole.startswith("-") else result
    if not re.fullmatch(r"[+-]?(?:\d+/\d+|\d+(?:\.\d*)?|\.\d+)", text):
        raise ValueError("Usa un número, decimal o fracción")
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("Número inválido") from exc


def equivalent(answer, expected):
    try:
        return parse_number(answer) == parse_number(expected)
    except ValueError:
        return False


def decimal_text(value):
    value = Fraction(value)
    denominator = value.denominator
    for prime in (2, 5):
        while denominator % prime == 0:
            denominator //= prime
    if denominator != 1:
        raise ValueError("La fracción no tiene decimal finito")
    from decimal import Decimal, localcontext

    with localcontext() as ctx:
        ctx.prec = 80
        return (
            format(Decimal(value.numerator) / Decimal(value.denominator), "f")
            .rstrip("0")
            .rstrip(".")
            if value.denominator != 1
            else str(value.numerator)
        )
