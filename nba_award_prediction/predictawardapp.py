import streamlit as st
import pandas as pd
import pickle
from pathlib import Path

trained_model = Path(__file__).parents[0] / 'models/mvptable_random_forest_v01.pkl'
trained_allstar_model = Path(__file__).parents[0] / 'models/allstarselection_random_forest_v02.pkl'
trained_new_allstar_model = Path(__file__).parents[0] / 'models/newformat_allstarselection_random_forest_v01.pkl'
player_bio_data = Path(__file__).parents[0] / 'data/raw/nba_current_player_bio.csv'

from modules.get_league_standings import get_league_standings
from modules.get_curr_mvp_table import get_curr_mvp_table
from modules.get_curr_allstars import get_curr_allstars
from modules.get_curr_allstars_newformat import get_curr_allstars_newformat

st.set_page_config(
    page_title="NBA Predictions",
    page_icon=":basketball:",
    layout="wide"
)

st.subheader("2025-26 NBA Regular Season Predictions")

# MVP Predictions
with open(trained_model, "rb") as model_file:
    model = pickle.load(model_file)

mvptable = get_curr_mvp_table(model)
st.session_state["mvptable"] = mvptable

# All-Star Prediction using Old Format
bio = pd.read_csv(player_bio_data)
st.session_state["player_bio"] = bio

with open(trained_allstar_model, "rb") as allstar_model_file:
    allstar_model = pickle.load(allstar_model_file)

weststarters, eaststarters, westbench, eastbench, intallstars = get_curr_allstars(allstar_model, bio)
st.session_state["weststarters"] = weststarters
st.session_state["eaststarters"] = eaststarters
st.session_state["westbench"] = westbench
st.session_state["eastbench"] = eastbench

@st.fragment()
def old_format_allstar():
    left_sel, gap_sel, right_sel, gap_sel2 = st.columns([1.5, 0.5, 1.5, 8.5], vertical_alignment="top")
    with left_sel:
        selectconf = st.radio(
            label="**Conference**",
            options=["West", "East"],
            index=0, key='selected_conf'
        )
    with right_sel:
        selecttype = st.radio(
            label="**Selection Type**",
            options=["Starters", "Bench"],
            index=0, key='selected_type'
        )

    if selectconf == 'West':
        if selecttype == 'Starters':
            st.markdown("*with 2 Backcourt(BC) and 3 Frontcourt(FC) players*")
            st.dataframe(weststarters, hide_index=True)
        elif selecttype == 'Bench':
            st.markdown("*with 2 Backcourt(BC), 3 Frontcourt(FC) and 2 Wildcards(WC)*")
            st.dataframe(westbench, hide_index=True)
    elif selectconf == 'East':
        if selecttype == 'Starters':
            st.markdown("*with 2 Backcourt(BC) and 3 Frontcourt(FC) players*")
            st.dataframe(eaststarters, hide_index=True)
        elif selecttype == 'Bench':
            st.markdown("*with 2 Backcourt(BC), 3 Frontcourt(FC) and 2 Wildcards(WC)*")
            st.dataframe(eastbench, hide_index=True)


# New Format All-Star Predictions
with open(trained_new_allstar_model, "rb") as model_file:
    new_allstar_model = pickle.load(model_file)

worldteam, usteam1, usteam2 = get_curr_allstars_newformat(new_allstar_model, bio)
st.session_state["worldteam"] = worldteam
st.session_state["usteam1"] = usteam1
st.session_state["usteam2"] = usteam2

@st.fragment()
def new_format_allstar():
    selectteam = st.radio(
        label="**All-Star Team**",
        options=["World", "US #1", "US #2"],
        index=0, key='selected_team', horizontal=True
    )
    if selectteam == 'World':
        st.dataframe(worldteam, hide_index=True)
    elif selectteam == 'US #1':
        st.dataframe(usteam1, hide_index=True)
    elif selectteam == 'US #2':
        st.dataframe(usteam2, hide_index=True)

tab1, tab2, tab3, tab4 = st.tabs([":chart_with_upwards_trend: Standings", ":crown: MVP Tracker", ":star: Old Format All-Stars", ":earth_africa: U.S. vs. World All-Stars"])

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
    st.dataframe(mvptable, hide_index=True)
    st.session_state["mvptable"] = mvptable

with tab3:
    old_format_allstar()

with tab4:
    with st.popover("What is the new All-Star game format ?"):
        st.markdown("""- This year's All-Star game is featuring two teams of U.S. players and
                    one team of international players called the World team. There will be
                    a round-robin tournament with each team having a minimum of eight players.""")
        st.markdown("""- The voting process remains the same as 12 players from each conference
                    will be selected, but for the first time without regard to position.""")
        st.markdown("""- If the voting does not result in the selection of 16 U.S. players
                    and eight international players, the commissioner will select additional players
                    to reach the minimum number for either group. In that case,
                    at least one team would have more than 8 players.""")
        st.markdown("""- The process for assigning players to the two U.S. teams will be determined at a later date.
                    But for the purpose of this study, the players are grouped based on team wins so that
                    U.S. Team #1 features players from teams with higher number of wins.""")
    new_format_allstar()
