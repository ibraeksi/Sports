import pandas as pd
import numpy as np


def all_time_td_stats(df, num_td, num_winpct):
    """
    Returns number of triple-doubles for each player
    df = Game logs for triple-doubles
    num_td = Filter for minimum number of triple-doubles
    num_winpct = Filter for minimum winning percentage in triple-double games
    """
    count = df['PLAYER'].value_counts().rename_axis('PLAYER').reset_index(name='TD')
    # Calculate number of wins in a triple-double
    windf = df.groupby(['PLAYER','RES']).agg({'DATE':'count'}).unstack().droplevel(0, axis=1).reset_index()
    windf = windf.fillna(0)
    windf[['W', 'L']] = windf[['W', 'L']].astype(int)
    # Calculate number of home games in a triple-double
    homedf = df.groupby(['PLAYER','LOC']).agg({'DATE':'count'}).unstack().droplevel(0, axis=1).reset_index()
    homedf = homedf.fillna(0)
    homedf[['AWAY', 'HOME', 'N']] = homedf[['AWAY', 'HOME', 'N']].astype(int)
    # Merge stats to original table
    countwins = pd.merge(count, windf, left_on="PLAYER", right_on="PLAYER", how="left", sort=False)
    homewins = pd.merge(countwins, homedf, left_on="PLAYER", right_on="PLAYER", how="left", sort=False)

    homewins['RANK'] = homewins['TD'].rank(ascending=False, method='min').apply(np.floor).astype(int)
    homewins[['FirstName','LastName', 'Jr']] = homewins['PLAYER'].str.split(' ',expand=True)
    homewins = homewins.sort_values(['TD', 'LastName', 'FirstName'], ascending=[False, True, True])
    homewins['WIN%'] = np.round(100*homewins['W'] / homewins['TD'],1)
    homewins['atHOME%'] = np.round(100*homewins['HOME'] / homewins['TD'],1)
    finaldf = homewins[['RANK', 'PLAYER', 'TD', 'W', 'L', 'WIN%', 'HOME', 'AWAY', 'N', 'atHOME%']].rename({'N': 'NEUTRAL'}, axis=1)

    return finaldf[(finaldf['TD'] >= num_td) & (finaldf['WIN%'] >= num_winpct)].reset_index(drop=True)
