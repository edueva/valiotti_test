import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

df_in = pd.read_csv('games.csv')
df = df_in.copy()
df.dropna(inplace = True)
df = df.query('Year_of_Release >=2000')
df['Year_of_Release'] = df.Year_of_Release.astype('int32')

year = df.Year_of_Release.unique()
year.sort()

platforms = df.Platform.unique()
platforms.sort()

ratings = df.Rating.unique()
ratings.sort()


# App layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([

    html.H1("Game platforms results overview", style={'text-align': 'center'}),
    html.H4("Select Platforms, Games Rating and Year range to compare platforms productivity over time", style={'text-align': 'center'}),
    html.Br(),
# Row with two checklists
    html.Div([
        html.Div([
            html.P("Select platforms:"),
            dcc.Checklist(id="slct_platforms",
                 options = platforms,
                value = ['DC','PS2'],
                 inline=True,
                 style={'width': "50%"}
                 )
            ], className="six columns"),
        html.Div([
            html.P("Select Ratings:"),
            dcc.Checklist(id="slct_rating",
                 options=ratings,
                          value = ['E'],
                          inline=True,
                 style={'width': "50%"}
                 )
            ], className="six columns"),
    ], className="row"),

#Container for games quantity
    html.Br(),
    html.Div(id='games_number_container', children=[]),
    html.Br(),
    
#Row wuth two graphs            
    html.Div([
        html.Div([
            html.H4('Games number by Year'),
            dcc.Graph(id='area_plot', figure={})
        ], className="six columns"),

        html.Div([
            html.H4('User score vs. Critic score'),
            html.P("Marker size corresponds to games quantity in respective category"),
            dcc.Graph(id='scatter_plot', figure={})
        ], className="six columns"),
    ], className="row"),
    
# Years selector    
    dcc.RangeSlider(id='years_slider',min = min(year), max = max(year), step = 1, value = [2000, 2011], marks={
        2000: {'label': '2000'},
        2002: {'label': '2002'},
        2004: {'label': '2004'},
        2006: {'label': '2006'},
        2008: {'label': '2008'},
        2010: {'label': '2010'},
        2012: {'label': '2012'},
        2014: {'label': '2014'},
        2016: {'label': '2016'}})
])

#Callbacs

@app.callback(
    [Output(component_id='games_number_container', component_property='children'),
     Output(component_id='area_plot', component_property='figure'),
     Output(component_id='scatter_plot', component_property='figure')],
    [Input(component_id='slct_platforms', component_property='value'),
    Input(component_id='slct_rating', component_property='value'),
    Input(component_id='years_slider', component_property='value')]
)

def display_area(selected_platforms, selected_ratings, selected_years):
    selected_platforms.sort()
    df_fig = df.query('Platform in @selected_platforms & Rating in @selected_ratings & (Year_of_Release >= @selected_years[0] & Year_of_Release <= @selected_years[1])')
    
    unique_games_num = f'Number of selected games is {df_fig.Name.nunique()}'
    
# Data for areaplot    
    dff = df_fig.groupby(['Year_of_Release','Platform'], as_index = False).agg({'Name':'nunique'})
    dff.sort_values(['Year_of_Release','Platform'], inplace = True)
# Data for scatteplot    
    df_scat = df_fig.query('User_Score != "tbd"') \
        .groupby(['Platform', 'User_Score', 'Critic_Score'], as_index = False) \
        .agg({'Name':'nunique'})    
    df_scat['User_Score'] = df_scat['User_Score'].astype('float32')
    
    fig1 = go.Figure()
    
    for plat in selected_platforms:
        try:
            fig1.add_trace(go.Scatter(
                x = dff.query('Platform == @plat').Year_of_Release,
                y = dff.query('Platform == @plat').Name,
                name = plat,
                hoverinfo='x+y',
                mode='lines',
                line=dict(width=0.5),
                stackgroup='one' # define stack group
            ))
        except:
            print('Some variable is None')
            
    fig1.update_layout()
    
    fig2 = px.scatter(df_scat, x="User_Score", y="Critic_Score", color="Platform", size = 'Name')
    
    return unique_games_num, fig1, fig2

app.run_server(debug=True, use_reloader=False)
