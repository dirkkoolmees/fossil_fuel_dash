import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Load Data
#Data from https://wesr.unep.org/downloader.(Consumption and production -> Resource Efficiency)
url = 'https://raw.githubusercontent.com/dirkkoolmees/maps-import-export-of-fossil-fuels-/master/Fossil_fuel_imp_exp.csv'

#Read data, skip first 3 rows since they contain general info.
data = pd.read_csv (url)

dropdown_labels = data.groupby(['Country', 'Year']).sum(numeric_only = True)

# Build App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
        html.H6("Fossil fuel import/export"),
        html.Div([
        html.H6("Data set"),
        dcc.Dropdown(
            id='column', clearable=False,
            value='Export (tonnes)',
            options=[
                {'label': c, 'value': c}
                for c in dropdown_labels.columns
            ]),
        ],style={'display': 'inline-block', 'width': '40px'}),  
        html.Div([
        html.H6("Year"),
        dcc.Slider(
        id='year-slider',
        min=data['Year'].min(),
        max=data['Year'].max(),
        value=data['Year'].max(),
        marks={str(year): {'label':str(year), 'style':{'color': 'blue', 'fontSize': 9,'writing-mode': 'vertical-lr','text-orientation': 'sideways-right'}} for year in data['Year'].unique()}
    ),
    html.Div(id='output-container-slider'),
    ],style={'display': 'inline-block', 'width': '800px'}),      
        html.Div([
        dcc.Graph(id='graph_1'),
    ],style={'display': 'inline-block', 'width': '200px'}),
     html.Div([
        dcc.Graph(id='graph_2'),
    ],style={'display': 'inline-block', 'width': '40%'})
],style={'display': 'inline-block', 'width': '1000px'})    

def create_graphs(column, value):
    filtered_df = data[data.Year == value]
    #Calculate average trade
    average = '{:,}'.format(int(data[column].sum()/data.shape[0]))

    map = go.Figure(data=go.Choropleth(
      locations = filtered_df['country_code'],
      z = filtered_df[column],
      text = filtered_df['Country'],
      colorscale = 'Reds',
      autocolorscale=False,
      reversescale=False,
      marker_line_color='darkgray',
      marker_line_width=0.5
))

    map.update_layout(
      title_text='Fossil Fuel ' + column + ' in '+ str(value) + ' (average: '+ str(average) + ' tonnes)',
      geo=dict(
          showframe=False,
          showcoastlines=False,
          projection_type='equirectangular'
      ),coloraxis_showscale=False,
      annotations = [dict(
        x=0.05,
        y=0.05,
        xref='paper',
        yref='paper',
        text='Source:<a href="https://wesr.unep.org/downloader">\
            UNEP</a>',
        showarrow = False
    )]
)

    top_15 = filtered_df.sort_values(column, ascending = False)

    bar = px.bar(top_15.head(15), x='Country', y=column, color=column, color_continuous_scale='Reds')

    bar.update_xaxes(title_text='')
    bar.update_yaxes(title_text='')
    bar.update_layout(title = 'Top 15 Countries')
    return map, bar


# Define callback to update graph
@app.callback(
    Output('output-container-slider', 'figure'),
    [Input("column", "value"), Input('year-slider', 'value')]
)
@app.callback(
    [Output('graph_1', 'figure'), Output('graph_2', 'figure')],
    [Input("column", "value"), Input('year-slider', 'value')]
)
def update(column, value):
    return create_graphs(column,value)



# Run app
if __name__ == '__main__':
  app.run_server()
