import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_curr_allstars_final(finaldf):
    """
    Uses the final season stats at the time of All-Star Selection for 2026 and
    returns a table with all-stars
    finaldf = Final predictions for 2026 All-Star
    """
    finalweststart = finaldf[finaldf['TYPE'] == 'WestStart'].drop('TYPE', axis=1).reset_index(drop=True)
    finaleaststart = finaldf[finaldf['TYPE'] == 'EastStart'].drop('TYPE', axis=1).reset_index(drop=True)
    finalwestbench = finaldf[finaldf['TYPE'] == 'WestBench'].drop('TYPE', axis=1).reset_index(drop=True)
    finaleastbench = finaldf[finaldf['TYPE'] == 'EastBench'].drop('TYPE', axis=1).reset_index(drop=True)

    return finalweststart, finaleaststart, finalwestbench, finaleastbench
