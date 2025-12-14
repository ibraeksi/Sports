import streamlit as st
import pandas as pd
from pathlib import Path

historical_data = Path(__file__).parents[0] / 'data/processed/nba_historical_triple_doubles_wlocations.csv'
team_locations = Path(__file__).parents[0] / 'data/raw/NBA_Stadium_Locations.csv'

from modules.get_curr_tripdub import get_curr_tripdub
from modules.plot_tripdub import plot_tripdub

st.set_page_config(
    page_title="NBA Triple-Doubles",
    page_icon=":basketball:",
    layout="wide"
)

st.subheader("NBA Career Triple-Double Analysis")

# All-Star Prediction using Old Format
historical_df = pd.read_csv(historical_data)
st.session_state["historical_df"] = historical_df

curr_df = get_curr_tripdub()
loc_df = pd.read_csv(team_locations)
curr_df['POS'] = curr_df.apply(lambda x: x['TEAM'] if x['LOC'] == 'HOME' else x['VS'], axis=1)
curr_df['LAT'] = curr_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LAT'])))
curr_df['LON'] = curr_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LON'])))
st.session_state["curr_df"] = curr_df

combined = pd.concat([historical_df, curr_df]).reset_index(drop=True)
st.session_state["combined"] = combined


tab1, tab2, tab3 = st.tabs([":chart_with_upwards_trend: All-Time TD Leaders", ":page_with_curl: All-Time TD Game Logs", ":round_pushpin: All-Time TD Locations"])

with tab1:
    count = combined['PLAYER'].value_counts().rename_axis('PLAYER').reset_index(name='TD')
    count['RANK'] = count.index + 1

    left_rank, right_rank = st.columns([4,8], vertical_alignment="top")
    with left_rank:
        st.dataframe(count[['RANK', 'PLAYER', 'TD']], hide_index=True)

with tab2:
    displaycols = ['DATE', 'PLAYER', 'TEAM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'RES', 'LOC', 'VS']
    playerselect = st.text_input("Filter for player")

    if playerselect is not None:
        df = combined[combined['PLAYER'].str.contains(playerselect)][displaycols]
    else:
        df = combined[displaycols]

    st.dataframe(df.sort_values('PTS', ascending=False), hide_index=True)

with tab3:
    st.plotly_chart(plot_tripdub(combined), use_container_width=False)
