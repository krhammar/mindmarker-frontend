import re

import requests
import streamlit as st

from backend_api import get_article_content
from article_math import format_math

WORDS_PER_MINUTE = 230
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((?:[^()]|\([^()]*\))*\)")

# Returns article text & defines loading params
@st.cache_data(ttl=3600, show_spinner="Loading article...")
def load_article(article_id):
    return get_article_content(article_id)

# Separate metadata block between --- lines from the article body
def split_front_matter(text):
    metadata = {}
    if text.startswith("---"):
        _, header, text = text.split("---", 2)
        for line in header.strip().splitlines():
            key, sep, value = line.partition(":")
            if sep:
                metadata[key.strip()] = value.strip().strip('"')
    return metadata, text.strip()

# Returns the intro and a list of (heading, text) for each ## section
def split_sections(body):
    body = LINK_PATTERN.sub(r"\1", body)
    body = format_math(body)
    body = re.sub(r"^# .*\n", "", body, count=1)
    parts = re.split(r"^## (.+)$", body, flags=re.MULTILINE)
    lead = parts[0].strip()
    sections = [(h.strip(), t.strip()) for h, t in zip(parts[1::2], parts[2::2])]
    return lead, sections

# Selected article is saved in session_state by home.py or explore.py
article_id = st.session_state.get("current_article_id")

if not article_id:
    st.warning("No article selected. Browse the library to choose one")
    if st.button("Browse Library"):
        st.switch_page("pages/explore.py")
    st.stop()

# Fetch & Display the article
try:
    content = get_article_content(article_id)
except requests.RequestException as error:
    st.error(f"Could not load the article: {error}")
    if st.button("Back to Explore"):
        st.switch_page("pages/explore.py")
    st.stop()

metadata, body = split_front_matter(content)
lead, sections = split_sections(body)

st.session_state["current_article_title"] = metadata.get("title", "this article")

lead_minutes = max(1, round(len(lead.split()) / WORDS_PER_MINUTE))
full_words = len(lead.split()) + sum(len(text.split()) for _, text in sections)
full_minutes = max(1, round(full_words / WORDS_PER_MINUTE))

st.caption((metadata.get("topic") or "Article").upper())
st.title(metadata.get("title", "Untitled Article"))

if metadata.get("description"):
    st.markdown(f"*{metadata['description']}*")

st.caption(
    f"{lead_minutes} min intro - {full_minutes} min full article - "
    f"{len(sections)} sections"
)

if st.button("Take the quiz", type="primary", key="quiz_top"):
    st.switch_page("pages/quiz.py")

st.divider()

# Body intro is always visible, sections collapsed
if lead:
    st.markdown(lead)
else:
    st.warning("This article has no content")

if sections:
    st.subheader("Keep reading")
    for heading, text in sections:
        with st.expander(heading):
            st.markdown(text)

st.divider()

# Attribution (required by CC BY-SA)
source_url = metadata.get("url")
if source_url:
    st.caption(
        f" Adapted from [Wikipedia]({source_url}) under "
        "[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). "
        "Links removed and sections reorganized"
    )

left, right = st.columns(2)

with left:
    if st.button("Back to Explore", use_container_width=True):
        st.switch_page("pages/explore.py")

with right:
    if st.button("Take the quiz", use_container_width=True):
        st.switch_page("pages/quiz.py")