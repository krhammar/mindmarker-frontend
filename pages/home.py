import random
import streamlit as st

#Temporary sample content; replace with backend data later
ARTICLES = [
    {
        "id": "study_001",
        "title": "How Sleep Supports Memory",
        "subject": "Psychology",
        "summary": (
            "Explore how sleep may influence learning "
            "and the retention of new information."
        ),
        "questions": 5,
        "minutes": 4,
    },
    {
        "id": "study_002",
        "title": "The Science of Learning",
        "subject": "Education",
        "summary": (
            "Discover research topics involving practice, "
            "feedback, and long-term knowledge retention."
        ),
        "questions": 5,
        "minutes": 5,
    },
    {
        "id": "study_003",
        "title": "Artificial Intelligence in Research",
        "subject": "Computer Science",
        "summary": (
            "Explore how researchers study the uses and "
            "limitations of artificial intelligence."
        ),
        "questions": 6,
        "minutes": 6,
    },
]

#Initialize temp session data
if "xp" not in st.session_state:
    st.session_state["xp"] = 0
if "completed_quizzes" not in st.session_state:
    st.session_state["completed_quizzes"] = []
if "answer_results" not in st.session_state:
    st.session_state["answer_results"] = []

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
            article = random.choice(ARTICLES)
            open_article(article["id"])

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
            round(sum(results)) / len(results) * 100
            if results
            else 0
        )

        col1, col2 = st.columns(2)
        col1.metric("Total XP", xp)
        col2.metric("Quizzes", completed)

        level = xp // 100 + 1
        progress = (xp % 100) / 100


        st.write(f"**Level {level}**")
        st.progress(progress)

        st.caption(f"{xp % 100}/100 XP till next level")
        st.caption(f"Session Accuracy: {accuracy}")

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
            st.caption(f"{article['subject'].upper()}")

            st.subheader(article["title"])
            st.write(article["summary"])

            st.caption(
                f"{article['questions']} questions"
                f"  .  {article['minutes']} min"
            )

            if st.button(
                "View Article",
                key=f"article_{article['id']}",
                use_container_width=True
            ):
                open_article(article["id"])

st.divider()

st.caption("WittyTitle      Learn Learn Learn Witty Description Oh My God")