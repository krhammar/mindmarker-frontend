# Points, levels, & quiz records

from datetime import datetime

XP_PER_CORRECT = {"easy": 10, "medium": 15, "hard": 25}
COMPLETION_BONUS = {"easy": 10, "medium": 20, "hard": 40}
PERFECT_BONUS_RATE = 0.5
XP_PER_LEVEL = 100
DIFFICULTIES = ["easy", "medium", "hard"]

# Title unlocked at each level
LEVEL_TITLES = [
    (1, "Curious Newcomer"),
    (3, "Apprentice"),
    (5, "Scholar"),
    (8, "Researcher"),
    (12, "Professor"),
    (20, "Sage")
]


def init_progress(state):
    state.setdefault("xp", 0)
    state.setdefault("completed_quizzes", [])
    state.setdefault("answer_results", [])
    state.setdefault("quiz_best", {}) #"article_id:difficulty" = best XP earned
    state.setdefault("quiz_history", []) # One record per finished attempt

# Levels & Titles
# Levels & Titles

def level_for(xp):
    return xp // XP_PER_LEVEL + 1

def title_for(level):
    title = LEVEL_TITLES[0][1]
    for required, name in LEVEL_TITLES:
        if level >= required:
            title = name
    return title

def next_title(level):
    for required, name in LEVEL_TITLES:
        if required > level:
            return required, name
    return None

def quiz_xp(difficulty, correct, total):
    xp = correct * XP_PER_CORRECT[difficulty] + COMPLETION_BONUS[difficulty]
    if total and correct == total:
        xp += round(xp * PERFECT_BONUS_RATE)
    return xp

# Streaks
# Streaks

def answer_streaks(results):
    current = best = 0
    for correct in results:
        current = current + 1 if correct else 0
        best = max(best, current)
    return current, best

def perfect_streaks(history):
    current = best = 0
    for attempt in history:
        current = current + 1 if attempt["correct"] == attempt["total"] else 0
        best = max(best, current)
    return current, best

# Stats
# Stats

def progress_stats(state):
    init_progress(state)
    history = state["quiz_history"]
    results = state["answer_results"]
    xp = state["xp"]
    level = level_for(xp)

    by_difficulty = {}
    for difficulty in DIFFICULTIES:
        attempts = [a for a in history if a["difficulty"] == difficulty]
        correct = sum(a["correct"] for a in attempts)
        total = sum(a["total"] for a in attempts)
        by_difficulty[difficulty] = {
            "attempts": len(attempts),
            "accuracy": round(correct / total * 100) if total else None
        }

    current_streak, best_streak = answer_streaks(results)
    current_perfect, best_perfect = perfect_streaks(history)

    return {
        "xp": xp,
        "level": level,
        "title": title_for(level),
        "next_title": next_title(level),
        "xp_into_level": xp % XP_PER_LEVEL,
        "quizzes_completed": len(state["completed_quizzes"]),
        "attempts": len(history),
        "articles": len({a["article_id"] for a in history}),
        "accuracy": round(sum(results) / len(results) * 100) if results else None,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "current_perfect_streak": current_perfect,
        "best_perfect_streak": best_perfect,
        "perfect_quizzes": sum(a["correct"] == a["total"] for a in history),
        "by_difficulty": by_difficulty
    }

# Badges (id, name, requirement, stats check)
# Badges (id, name, requirement, stats check)

# Easy, medium and hard for all finished for at least one article
def _has_full_set(history):
    done = {}
    for attempt in history:
        done.setdefault(attempt["article_id"], set()).add(attempt["difficulty"])
    return any(len(levels) == 3 for levels in done.values())

BADGES = [
    ("first_quiz", "First Steps", "Finish your first quiz",
     lambda s, h: s["attempts"] >= 1),
    ("perfect", "Perfectionist", "Get every question right in a quiz",
     lambda s, h: s["perfect_quizzes"] >= 1),
    ("hard_mode", "Brave Mind", "Finish a hard quiz",
     lambda s, h: s["by_difficulty"]["hard"]["attempts"] >= 1),
    ("hard_perfect", "Flawless Thinker", "Get a perfect score on a hard quiz",
     lambda s, h: any(a["difficulty"] == "hard" and a["correct"] == a["total"] for a in h)),
    ("streak_10", "On Fire", "Answer 10 questions in a row correctly",
     lambda s, h: s["best_streak"] >= 10),
    ("streak_25", "Unstoppable", "Answer 25 questions in a row correctly",
     lambda s, h: s["best_streak"] >= 25),
    ("explorer", "Explorer", "Take quizzes on 5 different articles",
     lambda s, h: _has_full_set(h)),
    ("bookworm", "Bookworm", "Complete 10 different quizzes",
     lambda s, h: s["quizzes_completed"] >= 10),
    ("level_5", "Rising Scholar", "Reach level 5",
     lambda s, h: s["level"] >= 5)
]

def earned_badges(state):
    stats = progress_stats(state)
    history = state["quiz_history"]
    return {badge_id for badge_id, _, _, test in BADGES if test(stats, history)}

def badge_names(badge_ids):
    return [name for badge_id, name, _, _ in BADGES if badge_id in badge_ids]


# Save a finished quiz. Retakes only award xp above prev best
def record_quiz(state, article_id, difficulty, results, title=None):
    init_progress(state)
    key = f"{article_id}:{difficulty}"
    correct, total = sum(results), len(results)
    badges_before = earned_badges(state)

    earned = quiz_xp(difficulty, correct, total)
    previous_best = state["quiz_best"].get(key, 0)
    awarded = max(0, earned - previous_best)

    old_level = level_for(state["xp"])
    state["xp"] += awarded
    state["quiz_best"][key] = max(previous_best, earned)
    state["answer_results"].extend(results)
    if key not in state["completed_quizzes"]:
        state["completed_quizzes"].append(key)
    state["quiz_history"].append({
        "article_id": article_id,
        "title": title or f"Article {article_id}",
        "difficulty": difficulty,
        "correct": correct,
        "total": total,
        "xp": awarded,
        "finished_at": datetime.now().strftime("%H:%M")
    })

    new_level = level_for(state["xp"])
    return {
        "correct": correct,
        "total": total,
        "perfect": total > 0 and correct == total,
        "earned": earned,
        "awarded": awarded,
        "repeat": previous_best > 0,
        "level": new_level,
        "level_up": new_level > old_level,
        "new_title": title_for(new_level) if title_for(new_level) != title_for(old_level) else None,
        "new_badges": badge_names(earned_badges(state) - badges_before),
        "celebrated": False
    }