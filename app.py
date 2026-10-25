##### Navigation Page #####

import streamlit as st

st.set_page_config(
    page_title="Mindmarker",
    page_icon="Assets/MindMarkerLogosmol.png",
    layout="wide"
)

# List of Page objects with references to page file addresses
pages = [
    st.Page(
        "pages/home.py",
        title="Home",
        icon=None
    ),

    st.Page(
        "pages/explore.py",
        title="Explore",
        icon=None
    ),

    st.Page(
        "pages/article.py",
        title="Article",
        visibility="hidden"
    ),

    st.Page(
        "pages/quiz.py",
        title="Quiz",
        visibility="hidden"
    ),

    st.Page(
        "pages/progress.py",
        title="Progress",
        icon=None
    )
]

# Streamlit function to create a navbar from our pages list (nifty huh)
st.navigation(pages).run()