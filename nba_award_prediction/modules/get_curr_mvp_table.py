import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_curr_mvp_table(model):
    """
    Retrieves current season stats using nba_api and returns a table with mvp candidates
    model = Trained machine learning model to predict mvp candidates
    """
    # Get current stats
    pl = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26').get_data_frames()[0]
    tm = leaguestandings.LeagueStandings(season='2025-26').get_data_frames()[0][['TeamID', 'TeamName', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

    # Merge stats for prediction
    pl = pl.dropna(subset=['PLAYER_ID']).reset_index(drop=True)
    df = pd.merge(pl, tm, left_on=['TEAM_ID'], right_on=['TeamID'], how='left')

    # Filter out non MVP level players
    df['GP_PCT'] = df['GP'] / (df['WINS'] + df['LOSSES'])
    df.loc[df['GP_PCT'] > 1, 'GP_PCT'] = 1

    df['MPG'] = df['MIN']/df['GP']
    df['PPG'] = df['PTS']/df['GP']

    df.drop(df.loc[df['MPG'] < 30].index, inplace=True)
    df.drop(df.loc[df['PPG'] < 10].index, inplace=True)

    df = df.reset_index(drop=True)
    df[['RPG', 'APG', 'TPG', 'SPG', 'BPG', 'FPG', 'PMPG']] = df[['REB', 'AST', 'TOV', 'STL', 'BLK', 'NBA_FANTASY_PTS', 'PLUS_MINUS']].div(df['GP'], axis=0)

    norm_df = df[['WinPCT', 'GP_PCT', 'MPG', 'PPG', 'RPG', 'APG', 'TPG', 'SPG', 'BPG', 'FPG', 'PMPG']].rank(pct = True)
    norm_df['PlayoffRank'] = df['PlayoffRank'].rank(pct=True, ascending=False)

    features = ['WinPCT', 'FPG', 'PlayoffRank']
    new_predictions = model.predict(norm_df[features])
    df['MVP'] = new_predictions

    proba_predict = model.predict_proba(norm_df[features])
    df[['PREDICT_NOT', 'PREDICT_PROB']] = pd.DataFrame(proba_predict)

    mvpdf = df.reset_index(drop=True)
    mvpdf['PREDICT_PROB'] = 100*mvpdf['PREDICT_PROB']

    mvptable = mvpdf[['PREDICT_PROB', 'PLAYER_NAME', 'AGE', 'GP', 'TeamName', 'W', 'L',
                      'Conference', 'PlayoffRank', 'WinPCT', 'WINS', 'LOSSES',
                      'GP_PCT', 'MPG', 'PPG', 'RPG', 'APG', 'TPG', 'SPG', 'BPG']].rename(
                          columns={'PLAYER_NAME':'PLAYER', 'TeamName':'TEAM', 'Conference':'CONF',
                                   'Record':'RECORD', 'WinPCT':'WIN%', 'PlayoffRank':'TEAMRANK',
                                   'MPG':'MIN', 'PPG':'PTS', 'RPG':'REB', 'APG':'AST', 'TPG':'TOV',
                                   'SPG':'STL', 'BPG':'BLK', 'PREDICT_PROB':'PROB%', 'GP_PCT':'GP%'})

    mvptable['AGE'] = mvptable['AGE'].astype(int)
    mvptable['TEAMRANK'] = '#'+mvptable['TEAMRANK'].astype(str)
    mvptable[['WIN%', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PROB%', 'GP%']] = mvptable[['WIN%', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PROB%', 'GP%']].round(2)

    mvptable['GP%'] = np.round(100*mvptable['GP%'],2)
    mvptable['RANK'] = mvptable['CONF'] + ' ' + mvptable['TEAMRANK']
    mvptable['RECORD'] = mvptable['WINS'].astype(str) + '-' + mvptable['LOSSES'].astype(str)

    colorder = ['PROB%', 'PLAYER', 'AGE', 'GP', 'GP%', 'W', 'L',
                'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'TEAM', 'RANK', 'RECORD']
    mvptable = mvptable[colorder].sort_values('PROB%', ascending=False).head(10).reset_index(drop=True)

    return mvptable
