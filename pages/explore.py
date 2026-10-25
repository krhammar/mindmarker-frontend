import requests
import streamlit as st

from backend_api import get_articles

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


st.title("Explore the Library")
st.caption("Find an article, discover a topic, and start learning")

st.divider()


def open_article(article):
    #Save the chosen article and navigate to its page
    article_id = article.get("id")
    if not article_id:
        st.error("This article is missing its identifier")
        return

    st.session_state["current_article_id"] = article_id
    st.switch_page("pages/article.py")

# Fetch articles

try:
    articles = get_articles()
except (requests.RequestException, ValueError) as error:
    st.error(f"Could not load the article library: {error}")
    st.stop()

if not articles:
    st.info("There are no articles to display yet.")
    st.stop()

# Search and topic filters

search_column, topic_column = st.columns([2, 1])

with search_column:
    search = st.text_input(
        "Search articles",
        placeholder="Seach titles and descriptions..."
    )

# Get available topics from the article metadata
topics = sorted({
    article.get("topic", "Other")
    for article in articles
    if isinstance(article, dict)
})

with topic_column:
    selected_topic = st.selectbox(
        "Topic",
        ["All topics"] + topics
    )

# Filter articles
filtered_articles = []

for article in articles:
    if not isinstance(article, dict):
        continue
    title = article.get("title", "")
    description = article.get("description", "")
    topic = article.get("topic", "Other")

    matches_search = search.lower() in (
        f"{title}{description}{topic}"
    ).lower()

    matches_topic = (
        selected_topic == "All topics"
        or topic == selected_topic
    )

    if matches_search and matches_topic:
        filtered_articles.append(article)

st.caption(f"{len(filtered_articles)} article(s) found")

results = st.empty()
with results.container():
    if not filtered_articles:
        st.info("No articles match your search. Try another keyword or topic.")
    else:
        for start in range(0, len(filtered_articles), 3):
            columns = st.columns(3)

            for offset, (column, article) in enumerate(
                zip(columns, filtered_articles[start:start + 3])
            ):
                with column:
                    with st.container(border=True):
                        # Article Title
                        st.caption(article.get("topic", "ARTICLE").upper())

                        st.subheader(article.get("title", "Untitled Article"))
                        # Article Summary
                        description = article.get("description")
                        if description:
                            st.write(description)
                        # Read article button
                        if st.button(
                            "Read Article",
                            key=f"read_{article.get('id', start)}",
                            use_container_width=True
                        ):
                            open_article(article)