import dash 
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
from datetime import datetime

# initialize datetime 
date = datetime.now().strftime("%d_%b_%Y")

vectorizer = CountVectorizer(stop_words='english')
df = pd.read_csv('../processed_data/news_' + date + '.csv')
df = df.iloc[np.random.permutation(len(df))]

app_colors = {
	'background': '#0C0F0A',
	'text': '#FFFFFF',
	'sentiment-plot':'#41EAD4',
	'volume-bar':'#FBFC74',
	'someothercolor':'#FF206E',
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash("Real-Time Australian News Analysis",external_stylesheets=external_stylesheets)
server = app.server

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
                style= {
                    'width' : '60%',
                    'verticalAlign' : 'middle',
				}
            )
        ],
        style={'display' : 'flex'}
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
		], style={'marginLeft': 100, 'fontSize': 16}
	),

],style={'padding': '20px'})

def topic_extractions(df):
	X_train = df['article']
	X_train_dtm = vectorizer.fit_transform(X_train)
	vocab = np.array(vectorizer.get_feature_names())

	"Generating Decomposition Model to extract topics"
	num_topics = 5
	num_top_words = 5
	clf = decomposition.NMF(n_components=num_topics,random_state=1)
	doctopic = clf.fit_transform(X_train_dtm)

	"Generating dominant topics for each words"
	topic_words = []
	for topic in clf.components_:
		word_idx = np.argsort(topic)[::-1][0:num_top_words]
		topic_words.append([vocab[i] for i in word_idx])

	# Making DataFrame that gets the doctopic (values of topics for each text)
	dftopic = pd.DataFrame(doctopic,columns=topic_words)
	dftopicinv=dftopic.T

	# Getting the dominant topic
	topic_series = []
	for i in np.arange(dftopic.shape[0]):
		topic_series.append(dftopicinv[i].idxmax())

	df['toptopic'] = topic_series

	# Getting top dominant topics and count them
	topic_count = df.toptopic.value_counts().rename_axis('vals').reset_index(name='count')
	topic_count['vals'] = topic_count['vals'].apply(lambda x: ",".join([i for i in x]))

	return topic_count


@app.callback(Output('live-update-graph', 'children'),
			[Input('source-news','value')])
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
		topics = topic_extractions(data)
		count_topics = topics['count']
		val_topics = topics['vals']
			
	else:
		count_topics = [0,0,0,0,0]
		val_topics = count_topics
		count_labels = [0,0,0]

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
							marker_colors=['rgba(184, 247, 212, 0.6)','rgba(255, 50, 50, 0.6)','rgba(131, 90, 241, 0.6)'],
							textinfo='value',
							hole=.65)
						],
						'layout':{
							'showlegend': True,
							'title':'Sentiment Analysis on News Articles',
							'annotations':[
								dict(
									text='{0:.2f}K'.format(sum(count_labels)/1000),
									font=dict(size=50),
									showarrow=False
								)
							]
						}
				}
			)
		],style={'width': '50%', 'display': 'inline-block', 'padding': '0 0 0 20'}),

		html.Div([
			dcc.Graph(
				id='topic_extract',
				figure={
					'data': [
						go.Bar(
							x=['Topic 1','Topic 2','Topic 3','Topic 4','Topic 5'], 
							y=count_topics,
							marker_color='rgb(158,202,225)', 
							marker_line_color='rgb(8,48,107)',
                  			marker_line_width=1.5, 
							opacity=0.6,
							hovertext=val_topics
						)],
						'layout':{
							'showlegend': False,
							'title':'Topic Extractions On News Articles', 
							
						}
				}
			)
		],style={'width': '50%', 'display': 'inline-block','padding': '0 0 0 20'})
	]

	return children

if __name__ == '__main__':
	app.run_server(debug=True)
