import os
from random import randint
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import flask
import pandas as pd
import pymongo

DATABASE_URL = os.environ.get('DATABASE_URL')
TABLE_NAME = os.environ.get('TABLE_NAME')
MONGO_URL = os.environ.get('MONGO_URL')
client = pymongo.MongoClient(MONGO_URL)
collection = client.db.news
df = pd.DataFrame(list(collection.find()))

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot': '#41EAD4',
    'volume-bar': '#FBFC74',
    'someothercolor': '#FF206E',
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Define app server
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash("Real-Time Australian News Analysis",
                external_stylesheets=external_stylesheets, server=server)

# App Layout
app.layout = html.Div(children=[
    html.H2('Real-Time Australian News Analysis', style={
        'textAlign': 'center'
    }),
    html.H5('(Last updated: May 04, 2020)', style={
        'textAlign': 'right'
    }),

    html.Div(
        [
            html.Div(
                [
                    html.H6("""Select source news""",
                            style={'margin-right': '2em'})
                ],
            ),

            dcc.Dropdown(
                id='source-news',
                options=[
                    {'label': 'ABC News', 'value': 'abc'},
                    {'label': 'Sydney Morning Herald', 'value': 'smh'}
                ],
                multi=True,
                value=['abc'],
                style={
                    'width': '60%',
                    'verticalAlign': 'middle',
                }
            )
        ],
        style={'display': 'flex'}
    ),

    html.Div(id='live-update-graph'),
    html.Div(id='live-update-graph-bottom'),

    # html.Div(
    # 	children = [
    # 		dcc.Slider(
    # 			id='num-articles',
    # 			min=5,
    # 			max=df.shape[0],
    # 			marks={i : '{}'.format(i) for i in range(0,df.shape[0],100)},
    # 			value=100,
    # 		),
    # 	],style = {'width': '50%','padding': '0 0 0 20'}
    # ),

    html.Div(
        className='row',
        children=[
            html.Div(
                className='three columns',
                children=[
                    html.P(
                        'Code avaliable at:'
                    ),
                    html.A(
                        'GitHub',
                        href='https://github.com/tranquanghuy0801/news_scraping'
                    )
                ]
            ),
            html.Div(
                className='three columns',
                children=[
                    html.P(
                        'Made with:'
                    ),
                    html.A(
                        'Dash / Plot.ly',
                        href='https://plot.ly/dash/'
                    )
                ]
            ),
            html.Div(
                className='three columns',
                children=[
                    html.P(
                        'Author:'
                    ),
                    html.A(
                        'Harry Tran',
                        href='https://www.linkedin.com/in/huy-quang-tran-983a89144/'
                    )
                ]
            )
        ], style={'marginLeft': 150, 'fontSize': 16}
    ),

], style={'padding': '20px'})


@app.callback(Output('live-update-graph', 'children'),
              [Input('source-news', 'value')])
def update_graph_live(source):
    # Select a subset of dataframe based on the value of slider
    if source:
        data = df[df['source'].isin(source)]
        # Count the number of sentiment labels
        df_labels = (data['label'].str.split(expand=True)
                     .stack()
                     .value_counts()
                     .rename_axis('vals')
                     .reset_index(name='count'))
        count_labels = df_labels['count']

        # do the topic extractions
        topics = data['toptopic'].value_counts().rename_axis(
            'vals').reset_index(name='count')
        topics['vals'] = topics['vals'].apply(
            lambda x: "".join(list(x)))
        count_topics = topics['count']
        val_topics = topics['vals']

    else:
        count_topics = [0, 0, 0, 0, 0]
        val_topics = [0, 0, 0, 0, 0]
        count_labels = [0, 0, 0]

    # Create visualization graph
    children = [
        html.Div([
            dcc.Graph(
                id='common_words',
                figure={
                    'data': [
                        go.Pie(
                            labels=['Positives', 'Negatives', 'Neutrals'],
                            values=count_labels,
                            name="View Metrics",
                            marker_colors=['rgba(184, 247, 212, 0.6)',
                                           'rgba(255, 50, 50, 0.6)', 'rgba(131, 90, 241, 0.6)'],
                            textinfo='value',
                            hole=.65)
                    ],
                    'layout':{
                        'showlegend': True,
                        'title': 'Sentiment Analysis on News Articles',
                        'annotations': [
                            dict(
                                text='{0:.2f}K'.format(
                                    sum(count_labels) / 1000),
                                font=dict(
                                    size=50),
                                showarrow=False
                            )
                        ]
                    }
                }
            )
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 0 0 20'}),

        html.Div([
            dcc.Graph(
                id='topic_extract',
                figure={
                    'data': [
                        go.Bar(
                            x=['Topic 1', 'Topic 2', 'Topic 3',
                                'Topic 4', 'Topic 5'],
                            y=count_topics,
                            marker_color='rgb(158, 202, 225)',
                            marker_line_color='rgb(8, 48, 107)',
                            marker_line_width=1.5,
                            opacity=0.6,
                            hovertext=val_topics
                        )],
                    'layout':{
                        'showlegend': False,
                        'title': 'Topic Extractions On News Articles',

                    }
                }
            )
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 0 0 20'})
    ]

    return children


# Main App Run
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
