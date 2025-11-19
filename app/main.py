import streamlit as st
from single_asset import run_single_asset_dashboard
from streamlit_autorefresh import st_autorefresh

# Refresh auto toutes les 5 minutes
st_autorefresh(interval=300000)

run_single_asset_dashboard()
