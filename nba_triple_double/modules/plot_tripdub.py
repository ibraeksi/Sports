import plotly.graph_objects as go

def plot_tripdub(df, team_names):
    """
    Creates a scattergeo plot showing triple-double counts per location
    df = Dataframe of all triple-doubles with their locations
    team_names = Team names and their abbreviations
    """
    grouped_df = df.groupby(['POS']).agg({'DATE': 'count', 'LAT': 'mean', 'LON': 'mean'}).reset_index().rename(columns={'DATE':'COUNT'})

    teamnamedict = {v: k for k, v in team_names.items()}

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
