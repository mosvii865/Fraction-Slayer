def score(stats):
    errors = stats["attempted"] - stats["correct"]
    accuracy_bonus = (
        round(300 * stats["correct"] / stats["attempted"]) if stats["attempted"] else 0
    )
    return max(
        0,
        stats["kills"] * 100
        + stats["correct"] * 150
        + stats["best_streak"] * 25
        + stats["secrets"] * 200
        + accuracy_bonus
        - errors * 20,
    )
