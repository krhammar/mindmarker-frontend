import random

import requests
import streamlit as st

from backend_api import get_quiz
from gamification import XP_PER_CORRECT, init_progress, record_quiz

DIFFICULTIES = {
    "easy": "Easy - intro",
    "medium": "Medium - full article",
    "hard": "Hard - comprehension"
}
NEXT_DIFFICULTY = {"easy": "medium", "medium": "hard"}


@st.cache_data(ttl=3600, show_spinner="Loading quiz...")
def load_quiz(article_id, difficulty):
    return get_quiz(article_id, difficulty)


# Quiz state callbacks (runs before page reruns)

def reset_quiz(quiz_key):
    st.session_state["quiz_key"] = quiz_key
    st.session_state["quiz_index"] = 0
    st.session_state["quiz_results"] = []
    st.session_state["quiz_choice"] = None
    st.session_state["quiz_summary"] = None
    st.session_state["quiz_attempt"] = st.session_state.get("quiz_attempt", 0) + 1

def check_answer(choice_key, answer_index):
    choice = st.session_state.get(choice_key)
    if choice is None:
        return
    st.session_state["quiz_choice"] = choice
    st.session_state["quiz_results"].append(choice == answer_index)

def next_question(total, article_id, difficulty):
    st.session_state["quiz_choice"] = None
    if st.session_state["quiz_index"] + 1 < total:
        st.session_state["quiz_index"] += 1
    else:
        st.session_state["quiz_summary"] = record_quiz(
            st.session_state, article_id,
            difficulty, st.session_state["quiz_results"],
            title=st.session_state.get("current_article_title")
        )

def change_difficulty(difficulty):
    st.session_state["quiz_difficulty"] = difficulty

def show_results(summary, article_id, difficulty, quiz_key):
    if not summary["celebrated"]:
        if summary["perfect"]:
            st.balloons()
        if summary["level_up"]:
            st.toast(f"Level up! You're now level {summary['level']}")
        if summary.get("new_title"):
            st.toast(f"New title unlocked: {summary['new_title']}")
        for badge in summary.get("new_badges", []):
            st.toast(f"Badge earned: {badge}")
        summary["celebrated"] = True

    st.subheader("Quiz complete!")

    score, xp, level = st.columns(3)
    score.metric("Score", f"{summary['correct']}/{summary['total']}")
    xp.metric("XP earned", f"+{summary['awarded']}")
    level.metric("Level", summary["level"])

    if summary["repeat"] and summary["awarded"] < summary["earned"]:
        st.caption(
            f"This attempt was worth {summary['earned']} XP. "
            "Retakes only award XP above your previous best."
        )
    if summary["perfect"]:
        st.success("Perfect score! +50% bonus XP")
        if summary.get("new_badges"):
            st.info("New badge: " + ", ".join(summary["new_badges"]))

    left, middle, right = st.columns(3)
    left.button("Retake quiz", on_click=reset_quiz, args=(quiz_key,), use_container_width=True)

    harder = NEXT_DIFFICULTY.get(difficulty)
    if harder:
        middle.button(
            f"Try {harder}",
            type="primary",
            on_click=change_difficulty,
            args=(harder,),
            use_container_width=True
        )

    if right.button("Back to article", use_container_width=True):
        st.switch_page("pages/article.py")
    if st.button("View your progress"):
        st.switch_page("pages/progress.py")

# Page
# Page
# Page

init_progress(st.session_state)



article_id = st.session_state.get("current_article_id")

if not article_id:
    st.warning("No article selected. Browse the library to choose one")
    if st.button("Browse Library"):
        st.switch_page("pages/explore.py")
    st.stop()

title = st.session_state.get("current_article_title", "this article")
st.title("Quiz")
st.caption(f"Test what you learned from {title}")

difficulty = st.radio(
    "Difficulty",
    list(DIFFICULTIES),
    format_func=DIFFICULTIES.get,
    horizontal=True,
    key="quiz_difficulty",
)
st.caption(
    f"{XP_PER_CORRECT[difficulty]} XP per correct answer -"
    "switching difficulty restarts the quiz"
)

# Start fresh when the article or difficulty changes
quiz_key = f"{article_id}:{difficulty}"
if st.session_state.get("quiz_key") != quiz_key:
    reset_quiz(quiz_key)

try:
    quiz = load_quiz(article_id, difficulty)
except requests.HTTPError as error:
    if error.response is not None and error.response.status_code == 404:
        st.info(f"There's no {difficulty} quiz for this article yet.")
    else:
        st.error(f"Could not load the quiz: {error}")
    st.stop()
except (requests.RequestException, ValueError) as error:
    st.error(f"Could not load the quiz: {error}")
    st.stop()

questions = quiz.get("questions", [])
if not questions:
    st.info("This quiz has no questions yet.")
    st.stop()

st.divider()

summary = st.session_state["quiz_summary"]
if summary:
    show_results(summary, article_id, difficulty, quiz_key)
    st.stop()

# Current question

total = len(questions)
index = st.session_state["quiz_index"]
question = questions[index]
options = question.get("options", [])
answer_index = question.get("answer_index", 0)
choice = st.session_state["quiz_choice"]

order = list(range(len(options)))
random.Random(f"{quiz_key}:{st.session_state['quiz_attempt']}:{index}").shuffle(order)

st.progress(index / total, text=f"Question {index + 1} of {total}")
st.subheader(question.get("question", ""))

if choice is None:
    # Answering
    choice_key = f"choice_{quiz_key}_{st.session_state['quiz_attempt']}_{index}"
    st.radio(
        "Choose an answer",
        order,
        format_func=lambda i: options[i],
        index=None,
        key=choice_key,
        label_visibility="collapsed",
    )
    st.button(
        "Check answer",
        type="primary",
        disabled=st.session_state.get(choice_key) is None,
        on_click=check_answer,
        args=(choice_key, answer_index),
    )
else:
    # Feedback
    for i in order:
        option = options[i]
        if i == answer_index:
            st.markdown(f"CORRECT - **{option}**")
        elif i == choice:
            st.markdown(f"INCORRECT - ~~{option}~~")
        else:
            st.markdown(f"<span style='opacity:0.5'>◻ {option}</span>", unsafe_allow_html=True)

    explanations = question.get("answer_explanations", [])
    if choice == answer_index:
        st.success(explanations[choice] if choice < len(explanations) else "Correct!")
    else:
        if choice < len(explanations):
            st.error(explanations[choice])
        if answer_index is not None and answer_index < len(explanations):
            st.info(explanations[answer_index])

    is_last = index + 1 == total
    st.button(
        "See results" if is_last else "Next question",
        type="primary",
        on_click=next_question,
        args=(total, article_id, difficulty),
    )