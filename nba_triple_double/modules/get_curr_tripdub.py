from requests import get
import pandas as pd


def get_curr_tripdub():
    """
    Retrieves current season triple-doubles
    """
    # The request url stated under the headers of the website
    url = 'https://stats.nba.com/stats/leaguegamelog'

    # The request header from the page
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Origin': 'https://www.nba.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.nba.com/',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true'
    }

    # The Query String Parameter from the page
    params = (
        ("Counter", '1000'),
        ("DateFrom", ''),
        ("DateTo", ''),
        ("Direction", 'DESC'),
        ("ISTRound", ''),
        ("LeagueID", '00'),
        ("PlayerOrTeam", 'P'),
        ("Season", '2025-26'),
        ('SeasonType', 'Regular Season'),
        ("Sorter", 'DATE'),
    )
    # Make a get request
    response = get(url, headers=headers, params=params)

    # Web request into JSON format
    jsn = response.json()

    # Reformat the JSON to DataFrame
    df = pd.DataFrame(jsn['resultSets'][0]['rowSet'])

    # Assigning column headers
    df.columns = jsn['resultSets'][0]['headers']

    tripdub = df[(df['PTS'] >= 10) & (df['REB'] >= 10) & ((df['AST'] >= 10) | (df['BLK'] >= 10))].reset_index(drop=True)

    tripdub[['TEAM','HOME', 'VS']] = tripdub['MATCHUP'].astype('str').str.split(' ',expand=True)
    tripdub['LOC'] = tripdub['HOME'].replace({'vs.':'HOME', '@': 'AWAY'})

    currdf = tripdub[['GAME_DATE', 'PLAYER_NAME', 'TEAM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'WL', 'LOC', 'VS']].rename(
        columns={'GAME_DATE':'DATE', 'PLAYER_NAME':'PLAYER', 'WL':'RES'})

    return currdf
