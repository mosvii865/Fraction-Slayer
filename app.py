"""Run: streamlit run app.py. The component remains mounted across reruns."""

import streamlit as st
from game.engine import GameEngine
from ui.game_component import game_component
from ui.styles import APP_CSS

st.set_page_config(
    page_title="Fraction Slayer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(APP_CSS, unsafe_allow_html=True)
if "engine" not in st.session_state:
    st.session_state.engine = GameEngine()
    st.session_state.reply = None
    st.session_state.last_event = None
event = game_component(st.session_state.reply)
if event and isinstance(event, dict) and event.get("id") != st.session_state.last_event:
    st.session_state.last_event = event.get("id")
    st.session_state.reply = st.session_state.engine.handle(event)
    if st.session_state.engine.state:
        st.session_state.statistics = st.session_state.engine.state["stats"].copy()
    st.rerun()
