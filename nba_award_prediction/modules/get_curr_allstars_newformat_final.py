import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_curr_allstars_newformat_final(finaldf):
    """
    Uses the final season stats at the time of All-Star Selection for 2026 and
    returns a table with all-stars according to the new format
    selectiondf = Final predictions for 2026 All-Star
    """
    # Per Conference
    eastselection = finaldf[finaldf['CONF'] == 'East'].head(12)
    westselection = finaldf[finaldf['CONF'] == 'West'].head(12)
    selectiondf = pd.concat([eastselection,westselection]).reset_index(drop=True)

    worldcolorder = ['PROB%', 'POS', 'PLAYER', 'COUNTRY', 'AGE', 'GP', 'GP%', 'TEAM', 'RANK', 'RECORD',
                   'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK']

    worldteam = selectiondf[selectiondf['COUNTRY'] != 'USA'][worldcolorder].sort_values('PROB%', ascending=False).reset_index(drop=True)
    # if len(worldteam) > 8:
    #     worldteam = worldteam[worldteam['PROB%'] >= 50].reset_index(drop=True)

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
