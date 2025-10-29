import pandas as pd
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import leaguedashplayerstats


def get_league_standings(conference):
    """
    Retrieves current season standings using nba_api
    conference = Conference Standings (West or East)
    """
    # Get current standings
    rankings = leaguestandings.LeagueStandings(season='2025-26').get_data_frames()[0]

    rankings['TEAM'] = rankings['TeamCity'] + ' ' + rankings['TeamName']
    df = rankings[['PlayoffRank', 'TEAM', 'TeamName', 'Conference', 'ConferenceRecord', 'Division', 'DivisionRecord', 'DivisionRank', 'WINS', 'LOSSES', 'WinPCT', 'Record', 'HOME', 'ROAD', 'L10']]

    df = df[df['Conference'] == conference].reset_index(drop=True)

    df = df[['PlayoffRank', 'TEAM', 'Record',
             'HOME', 'ROAD', 'L10', 'ConferenceRecord']].rename(columns={'Record':'RECORD', 'PlayoffRank':'RANK', 'WINS':'W', 'LOSSES':'L', 'ConferenceRecord':'CONF'})

    return df
