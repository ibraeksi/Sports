import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

historical_data = Path(__file__).parents[0] / 'data/processed/nba_historical_triple_doubles_wlocations.csv'
curr_data = Path(__file__).parents[0] / 'data/processed/nba_current_triple_doubles.csv'
team_locations = Path(__file__).parents[0] / 'data/raw/NBA_Stadium_Locations.csv'

from modules.get_curr_tripdub import get_curr_tripdub
from modules.plot_tripdub import plot_tripdub

st.set_page_config(
    page_title="NBA Triple-Doubles",
    page_icon=":basketball:",
    layout="wide"
)

st.subheader("NBA Career Triple-Double Analysis")

# All-Time Triple-Doubles
historical_df = pd.read_csv(historical_data)
st.session_state["historical_df"] = historical_df

# Current Season Triple-Doubles
curr_df = pd.read_csv(curr_data)
st.session_state["curr_df"] = curr_df

loc_df = pd.read_csv(team_locations)
curr_df['POS'] = curr_df.apply(lambda x: x['TEAM'] if x['LOC'] == 'HOME' else x['VS'], axis=1)
curr_df['LAT'] = curr_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LAT'])))
curr_df['LON'] = curr_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LON'])))
st.session_state["curr_df"] = curr_df

combined = pd.concat([historical_df, curr_df]).reset_index(drop=True)
st.session_state["combined"] = combined

teamnamedict = {'Dallas Mavericks': 'DAL', 'Orlando Magic': 'ORL', 'San Antonio Spurs': 'SAS',
                'Denver Nuggets': 'DEN', 'New Jersey Nets': 'NJN', 'Brooklyn Nets': 'BKN',
                'Chicago Packers': 'CHP', 'Chicago Zephyrs': 'CHZ', 'Baltimore Bullets': 'BAL',
                'Capitol Bullets': 'CAP', 'Washington Bullets': 'WSB', 'Washington Wizards': 'WAS',
                'Philadelphia Warriors': 'PHW', 'San Francisco Warriors': 'SFW', 'Golden State Warriors': 'GSW',
                'Buffalo Braves': 'BUF', 'San Diego Clippers': 'SDC', 'Los Angeles Clippers': 'LAC',
                'Minneapolis Lakers': 'MNL', 'Los Angeles Lakers': 'LAL', 'Vancouver Grizzlies': 'VAN',
                'Memphis Grizzlies': 'MEM', 'Milwaukee Bucks': 'MIL', 'Phoenix Suns': 'PHO',
                'Miami Heat': 'MIA', 'Indiana Pacers': 'IND', 'Detroit Pistons': 'DET',
                'New York Knicks': 'NYK', 'Portland Trail Blazers': 'POR', 'Oklahoma City Thunder': 'OKC',
                'Cleveland Cavaliers': 'CLE', 'Toronto Raptors': 'TOR', 'New Orleans Jazz': 'NOJ',
                'New Orleans Pelicans': 'NOP', 'Charlotte Hornets': 'CHA', 'Milwaukee Hawks': 'MLH',
                'St. Louis Hawks': 'STL', 'Atlanta Hawks': 'ATL', 'Minnesota Timberwolves': 'MIN',
                'Boston Celtics': 'BOS', 'San Diego Rockets': 'SDR', 'Houston Rockets': 'HOU',
                'Chicago Bulls': 'CHI', 'Utah Jazz': 'UTA', 'Syracuse Nationals': 'SYR',
                'Philadelphia 76ers': 'PHI', 'Seattle Supersonics': 'SEA', 'Rochester Royals': 'ROC',
                'Cincinnati Royals': 'CIN', 'Kansas City Kings': 'KCK', 'Sacramento Kings': 'SAC'}

tab1, tab2, tab3 = st.tabs([":chart_with_upwards_trend: All-Time TD Leaders", ":page_with_curl: All-Time TD Game Logs", ":round_pushpin: All-Time TD Locations"])

with tab1:
    count = combined['PLAYER'].value_counts().rename_axis('PLAYER').reset_index(name='TD')
    count['RANK'] = count['TD'].rank(ascending=False, method='min').apply(np.floor).astype(int)
    count[['FirstName','LastName', 'Jr']] = count['PLAYER'].str.split(' ',expand=True)
    count = count.sort_values(['TD', 'LastName'], ascending=[False, True])

    left_rank, right_rank = st.columns([4,8], vertical_alignment="top")
    with left_rank:
        st.dataframe(count[['RANK', 'PLAYER', 'TD']], hide_index=True)

with tab2:
    displaycols = ['DATE', 'PLAYER', 'TEAM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'RES', 'LOC', 'VS']
    selected_teams = st.multiselect("Filter by Team", teamnamedict.keys(),
                                 max_selections=5, width="stretch",
                                 accept_new_options=False, default=None)
    st.session_state["selected_teams"] = selected_teams

    if len(selected_teams) > 0:
        teamlist = []
        for team in selected_teams:
            teamlist.append(teamnamedict[team])
        df = combined[combined['TEAM'].isin(teamlist)][displaycols]
    else:
        df = combined[displaycols]

    st.dataframe(df.sort_values('PTS', ascending=False), hide_index=True)

with tab3:
    st.plotly_chart(plot_tripdub(combined, teamnamedict), use_container_width=False)
