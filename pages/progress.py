import streamlit as st

from gamification import (
    BADGES,
    DIFFICULTIES,
    XP_PER_LEVEL,
    earned_badges,
    init_progress,
    progress_stats
)

init_progress(st.session_state)
stats = progress_stats(st.session_state)
history = st.session_state["quiz_history"]
earned = earned_badges(st.session_state)

st.title("Your Progress")
st.caption("Progress is saved for this session only. Refreshing the page starts over.")

st.divider()

# Level card

with st.container(border=True):
    level_column, xp_column = st.columns([2, 1])

    with level_column:
        st.caption(f"LEVEL {stats['level']}")
        st.subheader(stats["title"])

    with xp_column:
        st.metric("Total XP", stats["xp"])

    st.progress(
        stats["xp_into_level"] / XP_PER_LEVEL,
        text=f"{stats['xp_into_level']}/{XP_PER_LEVEL} XP to level {stats['level'] + 1}"
    )

    if stats["next_title"]:
        next_level, next_name = stats["next_title"]
        st.caption(f"Reach level {next_level} to become a **{next_name}**")
    else:
        st.caption("You've unlocked every title!")

if not history:
    st.info("Finish your first quiz to start tracking your stats, streaks, and badges")
    if st.button("Find an article", type="primary"):
        st.switch_page("pages/explore.py")
else:
    # Stats
    st.subheader("Stats")

    quizzes, accuracy, streak, perfect = st.columns(4)
    quizzes.metric(
        "Quizzes completed",
        stats["quizzes_completed"],
        help=f"{stats['attempts']} attempts in total, including retakes"
    )
    accuracy.metric(
        "Accuracy",
        f"{stats['accuracy']}%" if stats["accuracy"] is not None else "-"
    )
    streak.metric(
        "Answer streak",
        stats["current_streak"],
        help=f"Correct answers in a row. Best: {stats['best_streak']}"
    )
    perfect.metric(
        "Perfect quizzes",
        stats["perfect_quizzes"],
        help=f"Best run of perfect quizzes in a row: {stats['best_perfect_streak']}"
    )
    st.caption(
        f"Best answer streak: **{stats['best_streak']}** -"
        f"Best perfect-quiz streak: **{stats['best_perfect_streak']}**"
    )

    st.markdown("**By difficulty**")
    for column, difficulty in zip(st.columns(3), DIFFICULTIES):
        numbers = stats["by_difficulty"][difficulty]
        with column:
            with st.container(border=True):
                st.caption(difficulty.upper())
                attempts = numbers["attempts"]
                st.write(f"{attempts} attempt{'s' if attempts != 1 else ''}")
                if numbers["accuracy"] is None:
                    st.progress(0.0, text="Not tried yet")
                else:
                    st.progress(numbers["accuracy"] / 100, text=f"{numbers['accuracy']}% correct")

# Badges

st.divider()
st.subheader("Badges")
st.caption(f"{len(earned)} of {len(BADGES)} earned")

badge_columns = st.columns(3)
for index, (badge_id, name, requirement, _) in enumerate(BADGES):
    with badge_columns[index % 3]:
        with st.container(border=True):
            if badge_id in earned:
                st.markdown(f"**{name}**")
                st.caption(f":green[**Earned**] - {requirement}")
            else:
                st.markdown(f"<span style='opacity:0.45'>**{name}**</span>", unsafe_allow_html=True)
                st.caption(f"Locked - {requirement}")

# Recent activity

if history:
    st.divider()
    st.subheader("Recent quizzes")

    for attempt in reversed(history[-10:]):
        score = f"{attempt['correct']}/{attempt['total']}"
        perfect_mark = " - perfect!" if attempt["correct"] == attempt["total"] else ""
        st.markdown(
            f"**{attempt['title']}** - {attempt['difficulty'].capitalize()} - "
            f"{score}{perfect_mark} - +{attempt['xp']} XP - {attempt['finished_at']}"
        )