# Points, levels, & quiz records

XP_PER_CORRECT = {"easy": 10, "medium": 15, "hard": 25}
COMPLETION_BONUS = {"easy": 10, "medium": 20, "hard": 40}
PERFECT_BONNUS_RATE = 0.5
XP_PER_LEVEL = 100

def init_progress(state):
    state.setdefault("xp", 0)
    state.setdefault("completed_quizzes", [])
    state.setdefault("answer_results", [])
    state.setdefault("quiz_best", {}) #"article_id:difficulty" = best XP earned

def level_for(xp):
    return xp // XP_PER_LEVEL + 1

def quiz_xp(difficulty, correct, total):
    xp = correct * XP_PER_CORRECT[difficulty] + COMPLETION_BONUS[difficulty]
    if total and correct == total:
        xp += round(xp * PERFECT_BONNUS_RATE)
    return xp

# Save a finished quiz. Retakes only award xp above prev best
def record_quiz(state, article_id, difficulty, results):
    init_progress(state)
    key = f"{article_id}:{difficulty}"
    correct, total = sum(results), len(results)

    earned = quiz_xp(difficulty, correct, total)
    previous_best = state["quiz_best"].get(key, 0)
    awarded = max(0, earned - previous_best)

    old_level = level_for(state["xp"])
    state["xp"] += awarded
    state["quiz_best"][key] = max(previous_best, earned)
    state["answer_results"].extend(results)
    if key not in state["completed quizzes"]:
        state["completed_quizzes"].append(key)

    return {
        "correct": correct,
        "total": total,
        "perfect": total > 0 and correct == total,
        "earned": earned,
        "awarded": awarded,
        "repeat": previous_best > 0,
        "level": level_for(state["xp"]),
        "level_up": level_for(state["xp"]) > old_level,
        "celebrated": False
    }