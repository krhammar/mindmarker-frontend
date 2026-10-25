import random
import streamlit as st
import requests

from backend_api import get_articles, get_random_article

from gamification import init_progress, level_for, XP_PER_LEVEL

# adds some weights to either side of the screen
st.markdown("""
<style>
/* Constrain the main content and center it */
.block-container {
    max-width: 1500px;
    padding-left: 2rem;
    padding-right: 2rem;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)


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

st.image("Assets/MindMarkerLogoblack.png", width=400)
#st.caption("Cool description that goes with WittyTitle")

st.divider()

st.write("Mindmarker is an innovative new gamified way to learn new topics and improve reading comprehension.")



st.divider()





# ===========================================






# Hero
# Hero
# Hero

# columns for xp tracking
left, right = st.columns([1.2, 1])

with left:
    st.header("Track your progress and earn XP.")
    st.caption("Mindmarker makes learning fun by letting users track their progress, complete quizzes, and earn XP as they explore new topics.")
    if st.button("View your stats"):
        st.switch_page("pages/progress.py")

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


st.divider();

# columns for article picking
left, right = st.columns([1.2, 1])

with left:
    with st.container(border=True):

        st.write("Start learning with a random article or browse our catalogue of 300 articles")

        #st.write("")

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
    
    st.header("Your next discovery awaits.")

    st.caption("Explore scholarly research, challenge your understanding, and earn xp as you learn")
  

    









# Featured Articles
# Featured Articles
# Featured Articles

st.divider()

st.header("Featured Articles")
st.write("Pick a topic and start learning")

article_columns = st.columns(3)

for index, article in enumerate(ARTICLES[:3]):
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

st.caption("MindMarker by Kyle Hammar, Matthew So, and Quinn Hunter")