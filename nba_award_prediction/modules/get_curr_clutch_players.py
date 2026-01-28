import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguedashplayerclutch
from nba_api.stats.endpoints import leaguedashteamclutch


def get_curr_clutch_players():
    """
    Retrieves current season stats using nba_api
    and returns a table with most clutch players
    """
    # Get current stats
    clutchplayer = leaguedashplayerclutch.LeagueDashPlayerClutch(
        per_mode_detailed='Totals',
        season='2025-26',
        season_type_all_star='Regular Season'
    ).get_data_frames()[0]

    clutchusage = leaguedashplayerclutch.LeagueDashPlayerClutch(
        measure_type_detailed_defense='Usage', # Focus on Usage metrics
        per_mode_detailed='PerGame',           # Or 'Totals'
        season='2025-26',
        season_type_all_star='Regular Season'
    ).get_data_frames()[0]

    clutchteam = leaguedashteamclutch.LeagueDashTeamClutch(
        per_mode_detailed='Totals',
        season='2025-26',
        season_type_all_star='Regular Season'
    ).get_data_frames()[0]

    midstep = clutchplayer.merge(clutchusage[['PLAYER_ID', 'PLAYER_NAME', 'NICKNAME', 'TEAM_ID', 'TEAM_ABBREVIATION', 'AGE', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'USG_PCT']], on='PLAYER_ID', suffixes=('_PL', '_USG'))
    merged = midstep.merge(clutchteam[['TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'MIN']], left_on='TEAM_ID_PL', right_on='TEAM_ID', suffixes=('_PL', '_TM')).rename(columns={'GP':'GP_TM', 'W':'W_TM', 'L':'L_TM', 'MIN':'MIN_TM'})

    merged['GP_PCT'] = merged['GP_PL'] / merged['GP_TM']
    merged['MIN_PCT'] = np.round(100*merged['MIN_PL'] / merged['MIN_TM'], 1)

    # Minimum criteria for qualification
    clutchdf = merged[(merged['USG_PCT'] > 0.2) & (merged['MIN_PCT'] >=70)].reset_index(drop=True)

    df = clutchdf[['PLAYER_NAME_PL', 'TEAM_ABBREVIATION_PL',
                   'GP_PL', 'MIN_PCT', 'W_PL', 'L_PL',
                   'MIN_PL', 'NBA_FANTASY_PTS', 'PTS',
                   'OREB', 'DREB', 'REB', 'AST', 'TOV',
                   'STL', 'BLK', 'PLUS_MINUS',
                   'USG_PCT', 'W_TM', 'L_TM']].rename(columns={'PLAYER_NAME_PL':'PLAYER',
                                                               'TEAM_ABBREVIATION_PL':'TEAM',
                                                               'NBA_FANTASY_PTS':'FP',
                                                               'GP_PL':'GP', 'W_PL':'W', 'L_PL':'L',
                                                               'MIN_PL':'MIN', 'PLUS_MINUS':'+/-',
                                                               'USG_PCT':'USG%', 'MIN_PCT':'MIN%'})

    df['RECORD'] = df['W_TM'].astype(str) + '-' + df['L_TM'].astype(str)
    df['FPM'] = df['FP'] / df['MIN']
    df['PPM'] = df['PTS'] / df['MIN']
    df['WIN%'] = np.round(100*df['W'] / (df['W'] + df['L']),2)
    df['MIN'] = np.round(df['MIN'],1)

    allclutch = df[(df['+/-']>0) & (df['WIN%']>=0.5)].sort_values(['FPM'], ascending=[False]).head(10).reset_index(drop=True)
    allclutch['RK'] = allclutch.index + 1

    for col in ['PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK']:
        allclutch[f"{col}/MIN"] = np.round(allclutch[col] / allclutch['MIN'],2)

    colorder = ['RK', 'PLAYER', 'TEAM', 'GP', 'W', 'L', 'WIN%', 'MIN',
                'PTS/MIN', 'REB/MIN', 'AST/MIN', 'TOV/MIN', 'STL/MIN', 'BLK/MIN', 'RECORD']
    allclutch = allclutch[colorder]

    return allclutch
