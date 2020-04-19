import dash 
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('../processed_data/abc_10_Apr_2020.csv')

app_colors = {
	'background': '#0C0F0A',
	'text': '#FFFFFF',
	'sentiment-plot':'#41EAD4',
	'volume-bar':'#FBFC74',
	'someothercolor':'#FF206E',
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
	html.H2('Real-Time Australian News Analysis', style={
		'textAlign': 'center'
	}),
	html.H5('(Last updated: April 19, 2020)', style={
		'textAlign': 'right'
	}),
	

	html.Div(id='live-update-graph'),
	html.Div(id='live-update-graph-bottom'),

	dcc.Slider(
			id='num-articles',
			min=5,
			max=df.shape[0],
			marks={0: '0',500: '500'},
			value=100,
			step=5
	),

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

@app.callback(Output('live-update-graph', 'children'),
			[Input('num-articles','value')])
def update_graph_live(n):
	# Select a subset of dataframe based on the value of slider
	data = df[:n]

	# Count the number of sentiment labels
	df_labels = (data['label'].str.split(expand=True)
							.stack()
						   	.value_counts()
					 		.rename_axis('vals')
						 	.reset_index(name='count'))

	# Create visualization graph
	children = [
		html.Div([
			dcc.Graph(
				id='common_words',
				figure={
					'data': [
							go.Pie(
								labels=['Positives', 'Negatives', 'Neutrals'], 
								values=df_labels['count'],
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
										text='{0:.1f}K'.format(sum(df_labels['count'])/1000),
										font=dict(
											size=50
										),
										showarrow=False
									)
								]
							}
				}
			)
		],style={'width': '50%', 'display': 'inline-block', 'padding': '0 0 0 20'})
	]

	return children

if __name__ == '__main__':
	app.run_server(debug=True)
