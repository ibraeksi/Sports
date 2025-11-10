import streamlit as st
import pandas as pd
import pickle
from pathlib import Path

trained_model = Path(__file__).parents[0] / 'models/undersampling_random_forest_v03.pkl'
trained_allstar_model = Path(__file__).parents[0] / 'models/allstarselection_random_forest_v02.pkl'
player_bio_data = Path(__file__).parents[0] / 'data/raw/nba_current_player_bio.csv'

from modules.get_league_standings import get_league_standings
from modules.get_curr_mvp_table import get_curr_mvp_table
from modules.get_curr_allstars import get_curr_allstars

st.set_page_config(
    page_title="NBA Award Predictions",
    page_icon=":basketball:",
    layout="wide"
)

st.subheader("2025-26 NBA Regular Season Award Predictions")

tab1, tab2, tab3, tab4, tab5 = st.tabs([":chart_with_upwards_trend: Standings", ":crown: MVP Tracker", ":star: West All-Stars", ":star: East All-Stars", ":earth_africa: International All-Stars"])

with tab1:
    left_sta, gap_sta, right_sta = st.columns([5.5, 1, 5.5], vertical_alignment="top")
    with left_sta:
        weststand = get_league_standings('West')
        st.markdown("Western Conference")
        st.dataframe(weststand, hide_index=True)
        st.session_state["weststand"] = weststand
    with right_sta:
        eaststand = get_league_standings('East')
        st.markdown("Eastern Conference")
        st.dataframe(eaststand, hide_index=True)
        st.session_state["eaststand"] = eaststand


with tab2:
    with open(trained_model, "rb") as model_file:
        model = pickle.load(model_file)

    mvptable = get_curr_mvp_table(model)
    st.dataframe(mvptable, hide_index=True)
    st.session_state["mvptable"] = mvptable

with tab3:
    bio = pd.read_csv(player_bio_data)
    st.session_state["player_bio"] = bio

    with open(trained_allstar_model, "rb") as allstar_model_file:
        allstar_model = pickle.load(allstar_model_file)

    weststarters, eaststarters, westbench, eastbench, intallstars = get_curr_allstars(allstar_model, bio)

    st.markdown(":red-background[Western Conference Starters] *with 2 Backcourt(BC) and 3 Frontcourt(FC) players*")
    st.dataframe(weststarters, hide_index=True)
    st.session_state["weststarters"] = weststarters

    st.markdown(":red-background[Western Conference Bench] *with 2 Backcourt(BC), 3 Frontcourt(FC) and 2 Wildcards(WC)*")
    st.dataframe(westbench, hide_index=True)
    st.session_state["westbench"] = westbench

with tab4:
    st.markdown(":blue-background[Eastern Conference Starters] *with 2 Backcourt(BC) and 3 Frontcourt(FC) players*")
    st.dataframe(eaststarters, hide_index=True)
    st.session_state["eaststarters"] = eaststarters

    st.markdown(":blue-background[Eastern Conference Bench] *with 2 Backcourt(BC), 3 Frontcourt(FC) and 2 Wildcards(WC)*")
    st.dataframe(eastbench, hide_index=True)
    st.session_state["eastbench"] = eastbench

with tab5:
    st.markdown("""This year's All-Star game is expected to feature a round-robin tournament
                with 2 USA teams and 1 World team consisting of 8 players each.
                It is not yet clear if player positions or conferences will play a role in the selection.
                But the following are the current top 10 international players as predicted using the model
                based on the selection criteria used in the All-Star tabs.""")
    st.dataframe(intallstars, hide_index=True)
    st.session_state["intallstars"] = intallstars
