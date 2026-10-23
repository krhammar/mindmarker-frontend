import random
import streamlit as st
import requests

from backend_api import get_articles, get_random_article

from gamification import init_progress, level_for, XP_PER_LEVEL

# Load articles from the backend 
try:
    ARTICLES = get_articles()

    #if isinstance(ARTICLES, dict):
    #    ARTICLES = ARTICLES.get("articles", [])
except (requests.RequestException, ValueError) as error:
    ARTICLES = []
    st.error(f"Could not load articles: {error}")

# Initialize temp session data
init_progress(st.session_state)

# Sets session id to the selected article & switches the page
def open_article(article_id):
    #Save the chosen article and navigate to its page
    st.session_state["current_article_id"] = article_id
    st.switch_page("pages/article.py")

# Header
# Header
# Header

st.title("WittyTitle")
st.caption("Cool description that goes with WittyTitle")

st.divider()

# Hero
# Hero
# Hero

left, right = st.columns([1.6, 1])

with left:
    st.subheader("Your next discovery awaits.")

    st.write("Explore scholarly research, challenge your understanding, and earn xp as you learn")


    button_randomArticle, button_browseArticles = st.columns(2)

    with button_randomArticle:
        if st.button(
            "Random Article",
            type="primary",
            use_container_width=True
        ):
            try:
                article = get_random_article()

                if article:
                    open_article(article["id"])
                else:
                    st.warning("No articles are available")
            except requests.RequestException as error:
                st.error(f"Could not load a random article: {error}")

    with button_browseArticles:
        if st.button(
            "Browse Library",
            use_container_width=True
        ):
            st.switch_page("pages/explore.py")

with right:
    with st.container(border=True):
        st.markdown("### Your Session")

        xp = st.session_state["xp"]
        completed = len (st.session_state["completed_quizzes"])
        results = st.session_state["answer_results"]

        accuracy = (
            round(sum(results) / len(results) * 100)
            if results
            else 0
        )

        col1, col2 = st.columns(2)
        col1.metric("Total XP", xp)
        col2.metric("Quizzes", completed)

        level = level_for(xp)
        progress = (xp % XP_PER_LEVEL) / XP_PER_LEVEL


        st.write(f"**Level {level}**")
        st.progress(progress)

        st.caption(f"{xp % XP_PER_LEVEL}/{XP_PER_LEVEL} XP till next level")
        st.caption(f"Session Accuracy: {accuracy}%")

# Featured Articles
# Featured Articles
# Featured Articles

st.divider()

st.header("Featured Articles")
st.write("Pick a topic and start learning")

article_columns = st.columns(2)

for index, article in enumerate(ARTICLES[:2]):
    with article_columns[index]:
        with st.container(border=True):
            st.caption((article.get("topic") or "Article").upper())

            st.subheader(article.get("title", "Untitled Article"))

            description = article.get("description")
            if description:
                st.write(description)

            if st.button(
                "View Article",
                key=f"article_{article.get('id', index)}",
                use_container_width=True
            ):
                open_article(article["id"])

st.divider()

st.caption("WittyTitle      Learn Learn Learn Witty Description Oh My God")