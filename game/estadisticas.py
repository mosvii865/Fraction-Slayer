def new_stats():
    return dict(
        kills=0,
        correct=0,
        attempted=0,
        streak=0,
        best_streak=0,
        seconds=0.0,
        secrets=0,
        damage=0,
        ammo_used=0,
    )


def register_answer(stats, correct):
    stats["attempted"] += 1
    if correct:
        stats["correct"] += 1
        stats["streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["streak"])
    else:
        stats["streak"] = 0


def accuracy(stats):
    return (
        round(100 * stats["correct"] / stats["attempted"], 1)
        if stats["attempted"]
        else 0.0
    )


def summary(stats):
    from .puntuacion import score

    return {**stats, "accuracy": accuracy(stats), "score": score(stats)}
