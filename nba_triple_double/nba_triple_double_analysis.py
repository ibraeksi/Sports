import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

historical_data = Path(__file__).parents[0] / 'data/processed/nba_historical_triple_doubles_wlocations.csv'
current_data = Path(__file__).parents[0] / 'data/processed/nba_current_triple_doubles.csv'
team_locations = Path(__file__).parents[0] / 'data/raw/NBA_Stadium_Locations.csv'

from modules.all_time_td_stats import all_time_td_stats
from modules.plot_tripdub import plot_tripdub
from modules.get_curr_tripdub import get_curr_tripdub

st.set_page_config(
    page_title="NBA Triple-Doubles",
    page_icon=":basketball:",
    layout="wide"
)

st.subheader("NBA Career Triple-Double Analysis")

# Read Triple-Doubles only once in the beginning
@st.cache_resource
def all_triple_doubles():
    # All-Time Triple-Doubles
    historical_df = pd.read_csv(historical_data)
    st.session_state["historical_df"] = historical_df

    # Current Season Triple-Doubles
    curr_df = pd.read_csv(current_data)
    st.session_state["curr_df"] = curr_df

    loc_df = pd.read_csv(team_locations)
    curr_df['POS'] = curr_df.apply(lambda x: x['TEAM'] if x['LOC'] == 'HOME' else x['VS'], axis=1)
    curr_df['LAT'] = curr_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LAT'])))
    curr_df['LON'] = curr_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LON'])))
    st.session_state["curr_df"] = curr_df

    return pd.concat([historical_df, curr_df]).reset_index(drop=True), len(curr_df)

combined, num_curr_td = all_triple_doubles()
st.session_state["combined"] = combined

# Update Current Triple-Doubles only if button is clicked
@st.cache_resource
def update_current_triple_doubles(latest_date, latest_num_td):
    update_df = get_curr_tripdub(latest_date, latest_num_td)
    if len(update_df) > 0:
        loc_df = pd.read_csv(team_locations)
        update_df['POS'] = update_df.apply(lambda x: x['TEAM'] if x['LOC'] == 'HOME' else x['VS'], axis=1)
        update_df['LAT'] = update_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LAT'])))
        update_df['LON'] = update_df['LOC'].map(dict(zip(loc_df['TEAM'], loc_df['LON'])))

    return update_df


teamnamedict = {'Dallas Mavericks': 'DAL', 'Orlando Magic': 'ORL', 'San Antonio Spurs': 'SAS',
                'Denver Nuggets': 'DEN', 'New Jersey Nets': 'NJN', 'Brooklyn Nets': 'BKN',
                'Chicago Packers': 'CHP', 'Chicago Zephyrs': 'CHZ', 'Baltimore Bullets': 'BAL', 'Baltimore Bullets': 'BLB',
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

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if "disabled" not in st.session_state:
    st.session_state.disabled = False

def click_button():
    st.session_state.clicked = True
    st.session_state.disabled = True


tab1, tab2, tab3 = st.tabs([":chart_with_upwards_trend: All-Time TD Leaders", ":page_with_curl: All-Time TD Game Logs", ":round_pushpin: All-Time TD Locations"])

with tab1:
    left_rank, gap_rank, right_rank = st.columns([3, 0.25, 8.75], vertical_alignment="top")
    with left_rank:
        num_td = st.slider("Min. Number of Triple-Doubles", 0, 210, 10)
        num_winpct = st.slider("Min. Winning % in Those Games", 0, 100, 50)

        last_available_date = combined['DATE'].max()
        st.session_state["last_date"] = last_available_date

        if st.session_state.clicked is False:
            st.markdown("\n\n")
            day_after_game = (pd.to_datetime(last_available_date, format='%Y-%m-%d') + pd.Timedelta(1, unit='D')).strftime('%Y-%m-%d')
            st.markdown(f"Last updated on {day_after_game}")

        last_game_date = (pd.Timestamp.today('US/Eastern') - pd.Timedelta(1, unit='D')).strftime('%Y-%m-%d')
        if last_game_date > combined['DATE'].max():
            if st.button("Update Current Season", on_click=click_button, disabled=st.session_state.disabled):
                latest_data = update_current_triple_doubles(last_available_date, num_curr_td)
                combined = pd.concat([combined, latest_data]).reset_index(drop=True)
                st.session_state["combined"] = combined
                st.session_state["last_date"] = last_game_date

                st.markdown("\n\n")
                today_date = pd.Timestamp.today('US/Eastern').strftime('%Y-%m-%d')
                st.markdown(f"Last updated on {today_date}")

    with right_rank:
        all_time_td_df = all_time_td_stats(combined, num_td, num_winpct)
        st.dataframe(all_time_td_df, hide_index=True)

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
