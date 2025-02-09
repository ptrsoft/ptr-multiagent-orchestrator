import imports
import streamlit as st

st.set_page_config(
    page_title="AWS Multi-Agent Orchestrator Demos",
    page_icon="👋",
)

pg = st.navigation(
    [
        st.Page("pages/home.py", title="Home", icon="🏠"),
        st.Page("movie-production/movie-production-demo.py", title="AI Movie Production Demo" ,icon="🎬"),
        st.Page("travel-planner/travel-planner-demo.py", title="AI Travel Planner Demo" ,icon="✈️"),
    ])
pg.run()