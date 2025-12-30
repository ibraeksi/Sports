import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_curr_allrookie_teams(model):
    """
    Retrieves current season stats using nba_api and returns a table with all-rookie teams
    model = Trained machine learning model to predict all-rookie teams
    """
    # Get current stats
    pl = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26').get_data_frames()[0]
    tm = leaguestandings.LeagueStandings(season='2025-26').get_data_frames()[0][['TeamID', 'TeamName', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

    curr_rooks = ['Ace Bailey', 'Brooks Barnhizer', 'Joan Beringer', 'Koby Brea', 'Johni Broome',
                  'Carter Bryant', 'Dylan Cardwell', 'Moussa Cisse', 'Walter Clayton Jr.', 'Nique Clifford',
                  'Javonte Cooke', 'Cedric Coward', 'Mohamed Diawara', 'Hunter Dickinson', 'Egor Dëmin',
                  'VJ Edgecombe', 'Noa Essengue', 'Jeremiah Fears', 'Cooper Flagg', 'Rasheer Fleming',
                  'Myron Gardner', 'Vladislav Goldin', 'Hugo González', 'Yang Hansen', 'Dylan Harper',
                  'Chucky Hepburn', 'DaRon Holmes II', 'Kasparas Jakučionis', 'Sion James', 'Tre Johnson',
                  'Curtis Jones', 'Kam Jones', 'David Jones Garcia', 'Ryan Kalkbrenner', 'Miles Kelly',
                  'Kon Knueppel', 'Yanic Konan Niederhäuser', 'Chaz Lanier', 'Caleb Love', 'Khaman Maluach',
                  'Chris Mañon', 'Alijah Martin', 'Jahmai Mashack', 'Liam McNeeley', 'Collin Murray-Boyles',
                  'Ryan Nembhard', 'Asa Newell', 'Lachlan Olbrich', 'Micah Peavy', 'Noah Penda', 'Taelon Peter',
                  'Drake Powell', 'Tyrese Proctor', 'Derik Queen', 'Maxime Raynaud', 'Will Richard',
                  'Jase Richardson', 'Will Riley', 'Hunter Sallis', 'Kobe Sanders', 'Ben Saraf', 'Mark Sears',
                  'Javon Small', 'Jahmyl Telfort', 'Adou Thiero', 'Ethan Thompson', 'Nolan Traore', 'Jamir Watkins',
                  'Amari Williams', 'Danny Wolf', 'Chris Youngblood']

    # Merge stats for prediction
    pl = pl[pl['PLAYER_NAME'].isin(curr_rooks)].reset_index(drop=True)
    pl = pl.dropna(subset=['PLAYER_ID']).reset_index(drop=True)
    df = pd.merge(pl, tm, left_on=['TEAM_ID'], right_on=['TeamID'], how='left')

    # Filter out non MVP level players
    df['GP_PCT'] = df['GP'] / (df['WINS'] + df['LOSSES'])
    df.loc[df['GP_PCT'] > 1, 'GP_PCT'] = 1

    df['MPG'] = df['MIN']/df['GP']
    df['PPG'] = df['PTS']/df['GP']

    df.drop(df.loc[df['GP_PCT'] < 0.5].index, inplace=True)
    df.drop(df.loc[df['MPG'] < 13].index, inplace=True)

    df = df.reset_index(drop=True)
    df[['RPG', 'APG', 'TPG', 'SPG', 'BPG', 'FPG', 'PMPG']] = df[['REB', 'AST', 'TOV', 'STL', 'BLK', 'NBA_FANTASY_PTS', 'PLUS_MINUS']].div(df['GP'], axis=0)

    norm_df = df[['W_PCT', 'WinPCT', 'GP_PCT', 'MPG', 'PPG', 'RPG', 'APG', 'TPG', 'SPG', 'BPG', 'FPG', 'PMPG']].rank(pct = True)
    norm_df['PlayoffRank'] = df['PlayoffRank'].rank(pct=True, ascending=False)

    features = ['PPG', 'FPG']
    new_predictions = model.predict(norm_df[features])
    df['ALL_ROOKIE'] = new_predictions

    proba_predict = model.predict_proba(norm_df[features])
    df[['PREDICT_NOT', 'PREDICT_PROB']] = pd.DataFrame(proba_predict)

    rookdf = df.reset_index(drop=True)
    rookdf['PREDICT_PROB'] = 100*rookdf['PREDICT_PROB']

    allrookie = rookdf[['PREDICT_PROB', 'PLAYER_NAME', 'AGE', 'GP', 'TeamName', 'W', 'L',
                      'Conference', 'PlayoffRank', 'WinPCT', 'WINS', 'LOSSES',
                      'GP_PCT', 'MPG', 'PPG', 'RPG', 'APG', 'TPG', 'SPG', 'BPG']].rename(
                          columns={'PLAYER_NAME':'PLAYER', 'TeamName':'TEAM', 'Conference':'CONF',
                                   'Record':'RECORD', 'WinPCT':'WIN%', 'PlayoffRank':'TEAMRANK',
                                   'MPG':'MIN', 'PPG':'PTS', 'RPG':'REB', 'APG':'AST', 'TPG':'TOV',
                                   'SPG':'STL', 'BPG':'BLK', 'PREDICT_PROB':'PROB%', 'GP_PCT':'GP%'})

    allrookie['AGE'] = allrookie['AGE'].astype(int)
    allrookie['TEAMRANK'] = '#'+allrookie['TEAMRANK'].astype(str)
    allrookie[['WIN%', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PROB%', 'GP%']] = allrookie[['WIN%', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PROB%', 'GP%']].round(2)

    allrookie['GP%'] = np.round(100*allrookie['GP%'],2)
    allrookie['RANK'] = allrookie['CONF'] + ' ' + allrookie['TEAMRANK']
    allrookie['RECORD'] = allrookie['WINS'].astype(str) + '-' + allrookie['LOSSES'].astype(str)

    colorder = ['PROB%', 'PLAYER', 'AGE', 'GP', 'GP%', 'W', 'L',
                'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'TEAM', 'RANK', 'RECORD']
    allrookie = allrookie[colorder].sort_values('PROB%', ascending=False).head(10).reset_index(drop=True)

    return allrookie
