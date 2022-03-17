import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash

url='https://drive.google.com/file/d/1QXvqgwjo_PJixFRcapKhjyca_Cd-58pr/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]

df_in = pd.read_csv(url)
df = df_in.copy()
df.dropna(inplace = True)
df = df.query('Year_of_Release >= 2000')

year = df.Year_of_Release.unique()
year.sort()

ratings = df.Rating.unique()
ratings.sort()

genre = df.Genre.unique()
genre.sort()


# App layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
#app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([

    html.H1("Game genres results overview", style={'text-align': 'center'}),
    html.H4("Select genres, rating and year range to compare game genres offering and success over time", style={'text-align': 'center'}),
    #html.Br(),
    
# Row with two checklists
    html.Div([
        html.Div([
            html.P("Select Genres:"),
            dcc.Checklist(id="slct_genres",
                 options = genre,
                value = ['Shooter','Strategy'],
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
    html.P(id='games_number_container', children=[]),
    #html.Br(),

# Row with Graph titles
    html.Div([
        html.Div([
            html.H4('Games number by Year'),
        ], className="six columns"),

        html.Div([
            html.H4('User score vs. Critic score'),
            html.P("Marker size corresponds to games number in respective category. Games with no User Score are not shown"),
        ], className="six columns"),
    ], className="row"),
    
#Row with two graphs            
    html.Div([
        html.Div([
            dcc.Graph(id='area_plot', figure={}, style = {'verticalAlign': 'top'}),
            # Years selector 
            dcc.RangeSlider(id='years_slider',min = min(year), max = max(year), step = 1, value = [2002, 2011], marks={
              2000: {'label': '2000'},
              2002: {'label': '2002'},
              2004: {'label': '2004'},
              2006: {'label': '2006'},
              2008: {'label': '2008'},
              2010: {'label': '2010'},
              2012: {'label': '2012'},
              2014: {'label': '2014'},
              2016: {'label': '2016'}})

        ], className="six columns"),

        html.Div([
            dcc.Graph(id='scatter_plot', figure={}, style = {'verticalAlign': 'bottom'})
        ], className="six columns"),
    ], className="row")
    
])

#Callbacs

@app.callback(
    [Output(component_id='games_number_container', component_property='children'),
     Output(component_id='area_plot', component_property='figure'),
     Output(component_id='scatter_plot', component_property='figure')],
    [Input(component_id='slct_genres', component_property='value'),
    Input(component_id='slct_rating', component_property='value'),
    Input(component_id='years_slider', component_property='value')]
)

def display_area(selected_genres, selected_ratings, selected_years):
    selected_genres.sort()
    df_fig = df.query('Genre in @selected_genres & Rating in @selected_ratings & (Year_of_Release >= @selected_years[0] & Year_of_Release <= @selected_years[1])')
    

    unique_games_num = f'Number of selected games is {df_fig.Name.nunique()}'
    
# Data for areaplot
    platforms = df_fig.Platform.unique() 
    dff = df_fig.groupby(['Year_of_Release','Platform'], as_index = False).agg({'Name':'nunique'}).rename(columns = {'Name':'Games_number'})
    
    dff.sort_values(['Year_of_Release','Platform'], inplace = True)
    
# Data for scatteplot    
    df_scat = df_fig.query('User_Score != "tbd"') \
        .groupby(['Genre', 'User_Score', 'Critic_Score'], as_index = False) \
        .agg({'Name':'nunique'}) \
        .rename(columns = {'Name':'Games_number'})
    
    df_scat['User_Score'] = df_scat['User_Score'].astype('float32')

# areaplot    
    fig1 = go.Figure()

    for plat in platforms:
      try:
        fig1.add_trace(go.Scatter(
                x = dff.query('Platform == @plat').Year_of_Release,
                y = dff.query('Platform == @plat').Games_number,
                name = plat,
                hoverinfo='x+y',
                mode='lines',
                line=dict(width=0.5),
                stackgroup='one'))
      except:
            print('Some variable is None')
            
    fig1.update_layout(#autosize=False,
                       #width=650,
                       xaxis=dict(title="Year"),
                       yaxis=dict(title="Games number"),
                       margin=dict(l=20, r=60, t=70, b=70),
                       #legend=dict(yanchor="top",
                       #            y=0.99,
                       #            xanchor="left",
                       #            x=0.01),
                       #showlegend=False
                       )
    
    #fig1.update_yaxes(automargin=True)

# scatteplot     
    fig2 = px.scatter(df_scat, x="User_Score", y="Critic_Score", color="Genre", size = 'Games_number',
                     labels={
                     "User_Score": "User score",
                     "Critic_Score": "Critic score",
                     "Games_number":"Games number"})
    fig2.update_layout(margin=dict(l=20, r=60, t=70, b=70),
                       #legend=dict(yanchor="top",
                       #            y=0.99,
                       #            xanchor="left",
                       #            x=-0.32
                      #           )
    )
    #fig2.update_yaxes(automargin=True)
    
    return unique_games_num, fig1, fig2


#app.run_server(mode='inline', port=8030)
app.run_server(port=8030)
