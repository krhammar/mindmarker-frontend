import requests
import streamlit as st

from backend_api import get_article_content

st.title("Article")

# Selected article is saved in session_state by home.py or explore.py
filename = st.session_state.get("current_article_id")

if not filename:
    st.warning("No article selected. Browse the library to choose one")
    if st.button("Browse Library"):
        st.switch_page("pages/explore.py")
    st.stop()

# Fetch & Display the article
try:
    content = get_article_content(filename)

    st.divider()

    if content.strip():
        st.markdown(content)
    else:
        st.warning("This article has no content")
except requests.RequestException as error:
    st.error(f"Could not load the article: {error}")

st.divider()

left, right = st.columns(2)

with left:
    if st.button("Back to Explore", use_container_width=True):
        st.switch_page("pages/explore.py")

with right:
    if st.button("Take a quiz", use_container_width=True):
        st.switch_page("pages/quiz.py")