import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_curr_allstars_newformat(model, bio):
    """
    Retrieves current season stats using nba_api and returns a table
    with all-stars according to the new format
    model = Trained machine learning model to predict all-stars
    bio = Player bios for adding position and country
    """
    # Get current stats
    pl = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26').get_data_frames()[0]
    tm = leaguestandings.LeagueStandings(season='2025-26').get_data_frames()[0][['TeamID', 'TeamName', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

    # Merge stats for prediction
    pl = pl.dropna(subset=['PLAYER_ID']).reset_index(drop=True)
    df = pd.merge(pl, tm, left_on=['TEAM_ID'], right_on=['TeamID'], how='left')

    posdict = dict(bio[['PERSON_ID', 'POSITION']].values)
    countrydict = dict(bio[['PERSON_ID', 'COUNTRY']].values)
    df['POS'] = df['PLAYER_ID'].map(posdict)
    df['COUNTRY'] = df['PLAYER_ID'].map(countrydict)
    df['CONF'] = df['Conference'].map({'West':'W', 'East':'E'})

    # Filter out non MVP level players
    df['GP_PCT'] = df['GP'] / (df['WINS'] + df['LOSSES'])
    df.loc[df['GP_PCT'] > 1, 'GP_PCT'] = 1

    df['MPG'] = df['MIN']/df['GP']
    df['PPG'] = df['PTS']/df['GP']

    df.drop(df.loc[df['MPG'] < 24].index, inplace=True)
    df.drop(df.loc[df['GP_PCT'] < 0.5].index, inplace=True)

    df = df.reset_index(drop=True)
    df[['RPG', 'APG', 'TPG', 'SPG', 'BPG', 'FPG', 'PMPG']] = df[['REB', 'AST', 'TOV', 'STL', 'BLK', 'NBA_FANTASY_PTS', 'PLUS_MINUS']].div(df['GP'], axis=0)

    conf_type = ['E', 'W']

    for conf in conf_type:
        nba_group = df[df['CONF'] == conf]
        df['PTS_' + conf] = nba_group['PPG'].rank(pct = True)
        df['FP_' + conf] = nba_group['FPG'].rank(pct = True)
        df['W_PCT_' + conf] = nba_group['WinPCT'].rank(pct = True)

    df = df.fillna(0)
    nbanowmod = df[['PLAYER_NAME', 'COUNTRY', 'CONF', 'GP_PCT', 'POS', 'PTS_E', 'FP_E',
                    'W_PCT_E', 'PTS_W', 'FP_W', 'W_PCT_W']].rename(columns={'PLAYER_NAME':'PLAYER'})

    # Predict All-Stars
    cols = nbanowmod.columns
    test_cols = cols.drop(['GP_PCT', 'COUNTRY', 'PLAYER', 'POS', 'CONF'])

    new_predictions = model.predict(nbanowmod[test_cols])
    proba_predict = model.predict_proba(nbanowmod[test_cols])

    nbanowmod['PREDICT'] = new_predictions
    nbanowmod[['PREDICT_NOT', 'PREDICT_E', 'PREDICT_W']] = pd.DataFrame(proba_predict)
    nbanowmod['PREDICT_PROB'] = 100*(1-nbanowmod['PREDICT_NOT'])
    allstarprob = dict(nbanowmod[['PLAYER','PREDICT_PROB']].values)
    df['PREDICT_PROB'] = df['PLAYER_NAME'].map(allstarprob)

    finaldf = df[['PREDICT_PROB', 'POS', 'PLAYER_NAME', 'COUNTRY', 'AGE', 'GP', 'TeamName', 'W', 'L',
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
    finaldf = finaldf.sort_values('PROB%', ascending=False).reset_index(drop=True)

    # Per Conference
    eastselection = finaldf[finaldf['CONF'] == 'East'].head(12)
    westselection = finaldf[finaldf['CONF'] == 'West'].head(12)
    selectiondf = pd.concat([eastselection,westselection]).reset_index(drop=True)

    worldcolorder = ['PROB%', 'POS', 'PLAYER', 'COUNTRY', 'AGE', 'GP', 'GP%', 'TEAM', 'RANK', 'RECORD',
                   'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK']

    worldteam = selectiondf[selectiondf['COUNTRY'] != 'USA'][worldcolorder].sort_values('PROB%', ascending=False).reset_index(drop=True)

    colorder = ['PROB%', 'POS', 'PLAYER', 'AGE', 'GP', 'GP%', 'TEAM', 'RANK', 'RECORD',
                'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK']

    usteam1 = selectiondf[selectiondf['COUNTRY'] == 'USA'].sort_values(['WINS', 'PROB%'], ascending=[False, False]).head(8).reset_index(drop=True)
    usteam2 = selectiondf[selectiondf['COUNTRY'] == 'USA'].sort_values(['WINS', 'PROB%'], ascending=[False, False]).iloc[8:].reset_index(drop=True)

    addusallstars = pd.DataFrame()
    if len(usteam2) < 8:
        addcount = 0
        i = 0
        allusallstars = finaldf[finaldf['COUNTRY'] == 'USA'].reset_index(drop=True)
        while len(usteam2) + addcount < 8:
            if allusallstars.loc[i, 'PLAYER'] not in list(usteam1['PLAYER']) + list(usteam2['PLAYER']):
                addusallstars = pd.concat([addusallstars, allusallstars.iloc[i:i+1]]).reset_index(drop=True)
                addcount += 1
            i += 1

    usteam2 = pd.concat([usteam2, addusallstars]).sort_values(['WINS', 'PROB%'], ascending=[False, False]).reset_index(drop=True)

    usteam1out = usteam1[colorder].sort_values('PROB%', ascending=False).reset_index(drop=True)
    usteam2out = usteam2[colorder].sort_values('PROB%', ascending=False).reset_index(drop=True)

    return worldteam, usteam1out, usteam2out
