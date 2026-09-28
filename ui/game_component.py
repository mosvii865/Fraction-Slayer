from pathlib import Path
import streamlit.components.v1 as components

_component = components.declare_component(
    "fraction_slayer", path=str(Path(__file__).parent / "frontend")
)


def game_component(reply=None):
    return _component(reply=reply, key="fraction_slayer_game", default=None)
