import sys
import os

# Ajoute la racine au PATH Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from single_asset import run_single_asset_dashboard

# Refresh auto simple
st.markdown(
    """
    <meta http-equiv="refresh" content="300">
    """,
    unsafe_allow_html=True
)

run_single_asset_dashboard()
