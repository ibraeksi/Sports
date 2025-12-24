import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playergamelog


def get_curr_tripdub():
    """
    Retrieves current season triple-doubles using nba_api and returns a table
    with game logs in the required format
    """
    # Find players with triple-double games in current season
    seasonstats = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26').get_data_frames()[0]
    tripdubdf = seasonstats[seasonstats['TD3'] > 0].reset_index(drop=True)
    playeriddict = dict(zip(tripdubdf['PLAYER_ID'], tripdubdf['PLAYER_NAME']))

    # Game logs for triple-double games
    df = pd.DataFrame()
    for id in list(playeriddict.keys()):
        temp = playergamelog.PlayerGameLog(player_id=id).get_data_frames()[0]
        temp['PLAYER_NAME'] = playeriddict[id]
        # Filter for games with triple-doubles
        temptd = temp[(temp['PTS'] >= 10) & (temp['REB'] >= 10) & ((temp['AST'] >= 10) | (temp['BLK'] >= 10))].reset_index(drop=True)
        # Append to triple-double dataframe
        df = pd.concat([df, temptd]).reset_index(drop=True)
        time.sleep(0.2)

    df[['TEAM','HOME', 'VS']] = df['MATCHUP'].astype('str').str.split(' ',expand=True)
    df['LOC'] = df['HOME'].replace({'vs.':'HOME', '@': 'AWAY'})
    df['DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date.astype(str)
    df = df.sort_values(['DATE']).reset_index(drop=True)

    outdf = df[['DATE', 'PLAYER_NAME',
                'TEAM', 'PTS', 'REB',
                'AST', 'STL', 'BLK',
                'WL', 'LOC', 'VS']].rename(columns={'PLAYER_NAME':'PLAYER', 'WL':'RES'})

    return outdf
