import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_curr_allstars(model, bio):
    """
    Retrieves current season stats using nba_api and returns a table with all-stars
    model = Trained machine learning model to predict all-stars
    bio = Player bios for adding position
    """
    # Get current stats
    pl = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26').get_data_frames()[0]
    tm = leaguestandings.LeagueStandings(season='2025-26').get_data_frames()[0][['TeamID', 'TeamName', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

    # Merge stats for prediction
    pl = pl.dropna(subset=['PLAYER_ID']).reset_index(drop=True)
    df = pd.merge(pl, tm, left_on=['TEAM_ID'], right_on=['TeamID'], how='left')

    posdict = dict(bio[['PERSON_ID', 'POSITION']].values)
    df['POS'] = df['PLAYER_ID'].map(posdict)

    # Rookie player positions
    rookieposdict = {'Ace Bailey':'SF', 'Amari Williams':'C', 'Asa Newell':'PF', 'Ben Saraf':'SG',
       'Brooks Barnhizer':'SG', 'Caleb Love':'SG', 'Carter Bryant':'SF', 'Cedric Coward':'SG',
       'Chaz Lanier':'SG', 'Chris Mañon':'SG', 'Chris Youngblood':'SG',
       'Collin Murray-Boyles':'PF', 'Cooper Flagg':'SF', 'David Jones Garcia':'SF',
       'Derik Queen':'C', 'Drake Powell':'SG', 'Dylan Cardwell':'C', 'Dylan Harper':'SG',
       'Egor Dëmin':'PG', 'Hugo González':'SF', 'Hunter Dickinson':'C', 'Hunter Sallis':'SG',
       'Jahmir Young':'PG', 'Jahmyl Telfort':'SF', 'Jamir Watkins':'SF',
       'Jase Richardson':'SG', 'Javon Small':'PG', 'Jeremiah Fears':'PG',
       'Joan Beringer':'C', 'Khaman Maluach':'C', 'Kobe Sanders':'SG', 'Kon Knueppel':'SF',
       'Liam McNeeley':'SF', 'Mark Sears':'PG', 'Maxime Raynaud':'C', 'Micah Peavy':'SG',
       'Miles Kelly':'PG', 'Mohamed Diawara':'PF', 'Moussa Cisse':'C', 'Myron Gardner':'SF',
       'Nique Clifford':'SG', 'Noah Penda':'SF', 'Nolan Traore':'PG', 'Rasheer Fleming':'PF',
       'Ryan Kalkbrenner':'C', 'Ryan Nembhard':'PG', 'Sion James':'SG', 'Taelon Peter':'SG',
       'Tre Johnson':'SG', 'Tyrese Proctor':'PG', 'Tyson Etienne':'PG', 'VJ Edgecombe':'SG',
       'Walter Clayton Jr.':'PG', 'Will Richard':'SG', 'Will Riley':'SF', 'Yang Hansen':'C',
       'Yanic Konan Niederhäuser':'C'}

    df.loc[df['POS'].isnull(), 'POS'] = df.loc[df['POS'].isnull(),'PLAYER_NAME'].map(rookieposdict)

    # Frontcourt / Backcourt based on position
    frontcourt = ['F', 'SF', 'PF', 'C', 'C-F', 'F-C']
    backcourt = ['G', 'G-F', 'F-G', 'PG', 'SG']

    i = -1
    for pos in df['POS']:
        i += 1
        if pos in frontcourt:
            df.loc[i, 'TYPE'] = 'F'
        elif pos in backcourt:
            df.loc[i, 'TYPE'] = 'B'

    df['CONF'] = df['Conference'].map({'West':'W', 'East':'E'})

    # Filter out non MVP level players
    df['GP_PCT'] = df['GP'] / (df['WINS'] + df['LOSSES'])
    df.loc[df['GP_PCT'] > 1, 'GP_PCT'] = 1

    df['MPG'] = df['MIN']/df['GP']
    df['PPG'] = df['PTS']/df['GP']

    df.drop(df.loc[df['MPG'] < 24].index, inplace=True)
    df.drop(df.loc[df['GP_PCT'] < 0.4].index, inplace=True)

    df = df.reset_index(drop=True)
    df[['RPG', 'APG', 'TPG', 'SPG', 'BPG', 'FPG', 'PMPG']] = df[['REB', 'AST', 'TOV', 'STL', 'BLK', 'NBA_FANTASY_PTS', 'PLUS_MINUS']].div(df['GP'], axis=0)

    pos_type = ['B', 'F']
    conf_type = ['E', 'W']

    for conf in conf_type:
        for pos in pos_type:
            nba_group = df[(df['TYPE'] == pos) & (df['CONF'] == conf)]
            df['PTS_' + conf + pos] = nba_group['PPG'].rank(pct = True)
            df['FP_' + conf + pos] = nba_group['FPG'].rank(pct = True)
            # df[df['YEAR'] == year, 'PM_' + conf + pos] = nba_group['PLUS_MINUS'].rank(pct = True)
            df['W_PCT_' + conf + pos] = nba_group['WinPCT'].rank(pct = True)

    df = df.fillna(0)
    nbanowmod = df[['PLAYER_NAME', 'CONF', 'GP_PCT', 'POS', 'TYPE', 'PTS_EB', 'FP_EB',
        'W_PCT_EB', 'PTS_EF', 'FP_EF', 'W_PCT_EF', 'PTS_WB', 'FP_WB',
        'W_PCT_WB', 'PTS_WF', 'FP_WF', 'W_PCT_WF']].rename(columns={'PLAYER_NAME':'PLAYER'})

    # Predict All-Stars
    cols = nbanowmod.columns
    test_cols = cols.drop(['PLAYER', 'POS', 'CONF', 'TYPE'])

    new_predictions = model.predict(nbanowmod[test_cols])
    proba_predict = model.predict_proba(nbanowmod[test_cols])

    nbanowmod['PREDICT'] = new_predictions
    nbanowmod[['PREDICT_NOT', 'PREDICT_EF', 'PREDICT_EB', 'PREDICT_WF', 'PREDICT_WB']] = pd.DataFrame(proba_predict)

    # Eastern Conference
    eastallstars = nbanowmod.sort_values('PREDICT_EB', ascending=False).head(2)['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_EF', ascending=False).head(3)['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_EB', ascending=False).iloc[2:4]['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_EF', ascending=False).iloc[3:6]['PLAYER'].to_list()

    eastwildcard = []
    for i in range(12):
        proballstar = nbanowmod[nbanowmod['CONF'] == 'E'].sort_values('PREDICT_NOT').reset_index(drop=True)
        if proballstar.loc[i, 'PLAYER'] in eastallstars:
            continue
        else:
            eastwildcard.append(proballstar.loc[i, 'PLAYER'])

    # Western Conference
    westallstars = nbanowmod.sort_values('PREDICT_WB', ascending=False).head(2)['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_WF', ascending=False).head(3)['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_WB', ascending=False).iloc[2:4]['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_WF', ascending=False).iloc[3:6]['PLAYER'].to_list()

    westwildcard = []
    for i in range(12):
        proballstar = nbanowmod[nbanowmod['CONF'] == 'W'].sort_values('PREDICT_NOT').reset_index(drop=True)
        if proballstar.loc[i, 'PLAYER'] in westallstars:
            continue
        else:
            westwildcard.append(proballstar.loc[i, 'PLAYER'])

    nbanowmod['PREDICT_PROB'] = 100*(1-nbanowmod['PREDICT_NOT'])
    allstarprob = dict(nbanowmod[['PLAYER','PREDICT_PROB']].values)
    df['PREDICT_PROB'] = df['PLAYER_NAME'].map(allstarprob)

    finaldf = df[['PREDICT_PROB', 'TYPE', 'PLAYER_NAME', 'AGE', 'GP', 'TeamName', 'W', 'L',
                        'Conference', 'PlayoffRank', 'WinPCT', 'WINS', 'LOSSES',
                        'GP_PCT', 'MPG', 'PPG', 'RPG', 'APG', 'TPG', 'SPG', 'BPG']].rename(
                            columns={'PLAYER_NAME':'PLAYER', 'TeamName':'TEAM', 'Conference':'CONF',
                                    'Record':'RECORD', 'WinPCT':'WIN%', 'PlayoffRank':'TEAMRANK',
                                    'MPG':'MIN', 'PPG':'PTS', 'RPG':'REB', 'APG':'AST', 'TPG':'TOV',
                                    'SPG':'STL', 'BPG':'BLK', 'PREDICT_PROB':'PROB%', 'GP_PCT':'GP%'})

    finaldf['AGE'] = finaldf['AGE'].astype(int)
    finaldf['TEAMRANK'] = '#'+finaldf['TEAMRANK'].astype(str)
    finaldf[['WIN%', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PROB%', 'GP%']] = finaldf[['WIN%', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PROB%', 'GP%']].round(2)

    finaldf['GP%'] = np.round(100*finaldf['GP%'],2)
    finaldf['RANK'] = finaldf['CONF'] + ' ' + finaldf['TEAMRANK']
    finaldf['RECORD'] = finaldf['WINS'].astype(str) + '-' + finaldf['LOSSES'].astype(str)

    finaldf['POS'] = finaldf['TYPE'].apply(lambda x: 'BC' if x=='B' else 'FC')

    # Starter or Bench
    eastlist = eastallstars + eastwildcard
    westlist = westallstars + westwildcard
    eaststarters = nbanowmod.sort_values('PREDICT_EB', ascending=False).head(2)['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_EF', ascending=False).head(3)['PLAYER'].to_list()
    weststarters = nbanowmod.sort_values('PREDICT_WB', ascending=False).head(2)['PLAYER'].to_list() + nbanowmod.sort_values('PREDICT_WF', ascending=False).head(3)['PLAYER'].to_list()
    eastbench = list(set(eastlist) - set(eaststarters))
    westbench = list(set(westlist) - set(weststarters))

    colorder = ['PROB%', 'POS', 'PLAYER', 'AGE', 'GP', 'GP%', 'TEAM', 'RANK', 'RECORD',
                'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK']

    finaleaststart = finaldf[finaldf['PLAYER'].isin(eaststarters)][colorder].sort_values(['POS', 'PROB%'], ascending=[True, False]).reset_index(drop=True)
    finalweststart = finaldf[finaldf['PLAYER'].isin(weststarters)][colorder].sort_values(['POS', 'PROB%'], ascending=[True, False]).reset_index(drop=True)
    finaleastbench = finaldf[finaldf['PLAYER'].isin(eastbench)][colorder].sort_values(['POS', 'PROB%'], ascending=[True, False]).reset_index(drop=True)
    finalwestbench = finaldf[finaldf['PLAYER'].isin(westbench)][colorder].sort_values(['POS', 'PROB%'], ascending=[True, False]).reset_index(drop=True)

    return finalweststart, finaleaststart, finalwestbench, finaleastbench
