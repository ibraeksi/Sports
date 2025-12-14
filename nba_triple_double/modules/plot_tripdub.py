import plotly.graph_objects as go

def plot_tripdub(df):
    """
    Creates a scattergeo plot showing triple-double counts per location
    df = Dataframe of all triple-doubles with their locations
    """
    grouped_df = df.groupby(['POS']).agg({'DATE': 'count', 'LAT': 'mean', 'LON': 'mean'}).reset_index().rename(columns={'DATE':'COUNT'})

    teamnamedict = {'DAL': 'Dallas Mavericks', 'ORL': 'Orlando Magic', 'SAS': 'San Antonio Spurs', 'DEN': 'Denver Nuggets',
                    'NJN': 'New Jersey Nets', 'BKN': 'Brooklyn Nets', 'CHP': 'Chicago Packers', 'CHZ': 'Chicago Zephyrs',
                    'BLB': 'Baltimore Bullets', 'BAL': 'Baltimore Bullets', 'CAP': 'Capitol Bullets', 'WSB': 'Washington Bullets',
                    'WAS': 'Washington Wizards', 'PHW': 'Philadelphia Warriors', 'SFW': 'San Francisco Warriors', 'GSW': 'Golden State Warriors',
                    'BUF': 'Buffalo Braves', 'SDC': 'San Diego Clippers', 'LAC': 'Los Angeles Clippers', 'MNL': 'Minneapolis Lakers', 'LAL': 'Los Angeles Lakers',
                    'VAN': 'Vancouver Grizzlies', 'MEM': 'Memphis Grizzlies', 'MIL': 'Milwaukee Bucks', 'PHO': 'Phoenix Suns', 'MIA': 'Miami Heat',
                    'IND': 'Indiana Pacers', 'DET': 'Detroit Pistons', 'NYK': 'New York Knicks', 'POR': 'Portland Trail Blazers',
                    'OKC': 'Oklahoma City Thunder', 'CLE': 'Cleveland Cavaliers', 'TOR': 'Toronto Raptors', 'NOJ': 'New Orleans Jazz',
                    'NOP': 'New Orleans Pelicans', 'CHA': 'Charlotte Hornets', 'MLH': 'Milwaukee Hawks', 'STL': 'St. Louis Hawks',
                    'ATL': 'Atlanta Hawks', 'MIN': 'Minnesota Timberwolves', 'BOS': 'Boston Celtics', 'SDR': 'San Diego Rockets',
                    'HOU': 'Houston Rockets', 'CHI': 'Chicago Bulls', 'UTA': 'Utah Jazz', 'SYR': 'Syracuse Nationals',
                    'PHI': 'Philadelphia 76ers', 'SEA': 'Seattle Supersonics', 'ROC': 'Rochester Royals', 'CIN': 'Cincinnati Royals',
                    'KCK': 'Kansas City Kings', 'SAC': 'Sacramento Kings'}

    grouped_df['NAME'] = grouped_df['POS'].map(teamnamedict)
    grouped_df['TEXT'] = grouped_df['COUNT'].astype(str) + ' at ' + grouped_df['NAME']

    fig = go.Figure(data=go.Scattergeo(
        lat = grouped_df['LAT'],
        lon = grouped_df['LON'],
        text = grouped_df['TEXT'],
        mode = 'markers',
        marker = dict(
            size = grouped_df['COUNT']/3,
            opacity = 0.8,
            autocolorscale = False,
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = 'solar',
            cmin = 0,
            cmax = 250,
            color = grouped_df['COUNT'],
            colorbar=dict(
                orientation='h', y=-0.2,
                title=dict(
                    text='Total TD',
                )
            )
        )
    ))

    fig.update_layout(
        height=500, width=800,
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        geo = dict(
            scope='usa',
        ),
    )

    return fig
