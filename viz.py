import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import geopandas as gpd


import pandas as pd

# Load data from Excel
df = pd.read_excel('Block_data.xlsx')
gdf = gpd.read_file('set_data/lat_long.shp')
df_district = pd.read_excel('set_data/district_data.xlsx')



df.fillna(0, inplace=True)
df_district.fillna(0, inplace=True)

df_district = df_district[['State','District','state_dis',' Percentage  tap water connectionConnection','Perc HH Connection_reported', 'Perc HH Connection_certified',
       'Reporting Rate of HH with Tap Connection',
       'Certification Rate of HH with Tap Connection',
       'Certification Rate of Reported HH', 'Year', 'lat_long']]

df_district.rename(columns={'State':'State1','District':'District1',' Percentage  tap water connectionConnection':'Percentage  tap water connectionConnection','Perc HH Connection_reported':'Perc HH Connection Reported','Perc HH Connection_certified' : 'Perc HH Connection Certified'},inplace=True)


df['State'] = df['State'].str.title()
df['District'] = df['District'].str.title()
df['Block'] = df['Block'].str.title()

df_district['State1'] = df_district['State1'].str.title()
df_district['District1'] = df_district['District1'].str.title()

gdf['STATE'] = gdf['STATE'].str.title()


original_states = ['Andaman & Nicobar Islands', 'Dadra & Nagar Haveli And Daman & Diu', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
                   'Jammu & Kashmir']

new_states = ['Andaman & Nicobar', 'Dadra & Nagar Haveli & Daman & Diu','Jammu And Kashmir']

state_mapping = dict(zip(original_states, new_states))

# Replace values in the "STATE" column
gdf['STATE'] = gdf['STATE'].replace(state_mapping)

gdf.rename(columns={"STATE":"State",' Percentage  tap water connectionConnection':'Percentage  tap water connectionConnection'},inplace=True)


gdf.merge(df_district,on='lat_long',how='left').groupby('State')['District'].agg(list).reset_index()

gdf = gdf.merge(df_district,on='lat_long',how='left')

gdf.rename(columns={"STATE":"State",' Percentage  tap water connectionConnection':'Percentage  tap water connectionConnection'},inplace=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

app.layout = html.Div([
    # First row with the first dropdown and second dropdown
    html.Div([
        html.Div([
            html.Label("Select State:"),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df['State'].unique())],
                value=df['State'].unique()[0],
                className='dropdown'
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Select District:"),
            dcc.Dropdown(id='district-dropdown', className='dropdown'),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    # Second row with the third dropdown and fourth dropdown
    html.Div([
        html.Div([
            html.Label("Select Result Metric:"),
            dcc.Dropdown(
                id='result-metric-dropdown',
                options=sorted([
                    {'label': 'Percentage tap water Connection', 'value': 'Percentage  tap water connectionConnection'},
                    {'label': 'Perc HH Connection Reported', 'value': 'Perc HH Connection Reported'},
                    {'label': 'Perc HH Connection Certified', 'value': 'Perc HH Connection Certified'},
                    {'label': 'Reporting Rate of HH with Tap Connection', 'value': 'Reporting Rate of HH with Tap Connection'},
                    {'label': 'Certification Rate of HH with Tap Connection', 'value': 'Certification Rate of HH with Tap Connection'},
                    {'label': 'Certification Rate of Reported HH', 'value': 'Certification Rate of Reported HH'}
                ], key=lambda x: x['label']),
                value='Percentage  tap water connectionConnection',
                className='dropdown'
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in sorted(df['Year'].unique())],
                value=df['Year'].unique()[0],
                className='dropdown'
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    # Fourth row with the choropleth map and the first bar chart
    html.Div([
        html.Div([
            dcc.Graph(id='second-bar-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='choropleth-map')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    # Third row with the second bar chart
    html.Div([
        html.Div([
            dcc.Graph(id='bar-chart')
        ], style={'width': '100%','display': 'inline-block', 'padding': '10px'}),
    ]),
])


# Define callback to update district dropdown based on selected state
@app.callback(
    Output('district-dropdown', 'options'),
    [Input('state-dropdown', 'value')]
)
def update_district_dropdown(selected_state):
    districts = df[df['State'] == selected_state]['District'].unique()
    return [{'label': district, 'value': district} for district in sorted(districts)]

# Define callback to update bar chart based on selected state, district, result metric, and year
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('state-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('result-metric-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_bar_chart(selected_state, selected_district, selected_metric, selected_year):
    filtered_df = df[(df['State'] == selected_state) & (df['District'] == selected_district) & (df['Year'] == selected_year)]
    
    # Create a bar chart with formatted text values
    fig = go.Figure()
    fig.add_trace(go.Bar(x=filtered_df['Block'], y=filtered_df[selected_metric],
                        text=[f"{value:.2f}" if value != 0 else "0" for value in filtered_df[selected_metric]],
                        textposition='outside',
                        marker_color='blue',  # You can customize the color if needed
                        ))

    # Update layout
    fig.update_layout(
        title=f'Results for {selected_district}, {selected_state} - {selected_year}',
        xaxis=dict(title='Block'),
        yaxis=dict(title=selected_metric),
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig


@app.callback(
    Output('second-bar-chart', 'figure'),
    [Input('state-dropdown', 'value'),
     Input('result-metric-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_second_bar_chart(selected_state, selected_metric, selected_year):
    # Filter the GeoDataFrame based on the selected state and year
    filtered_df_district = df_district[(df_district['State1'] == selected_state) & (df_district['Year'] == selected_year)]

    # Create a bar chart with formatted text values
    fig = go.Figure()
    fig.add_trace(go.Bar(x=filtered_df_district['District1'], y=filtered_df_district[selected_metric],
                        text=[f"{value:.2f}" if value != 0 else "0" for value in filtered_df_district[selected_metric]],
                        textposition='outside',
                        marker_color='green',  # You can customize the color if needed
                        ))

    # Update layout
    fig.update_layout(
        title=f'Results for {selected_state} - {selected_year}',
        xaxis=dict(title='District1'),
        yaxis=dict(title=selected_metric),
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig


@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('state-dropdown', 'value'),
     Input('result-metric-dropdown', 'value'),
    Input('year-dropdown', 'value')]
)
def update_choropleth_map(selected_state, selected_metric,selected_year):
    # Filter the GeoDataFrame based on the selected state
    filtered_gdf = gdf[(gdf['State'] == selected_state) & (gdf['Year'] == selected_year)].to_crs('EPSG:4326')

    # Create the choropleth map
    fig = px.choropleth(
        filtered_gdf,
        geojson=filtered_gdf.geometry,
        locations=filtered_gdf.index,
        color=selected_metric,
        color_continuous_scale='blues',  # You can customize the color scale
        hover_name='District',
        labels={selected_metric: selected_metric},
        title=f'Choropleth Map for {selected_state} - {selected_metric}',
        range_color=(0, 100),
        color_continuous_midpoint=50
    )

    # Update layout
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=80),
        coloraxis_colorbar=dict(
            orientation='h'  # Set orientation to 'h' for horizontal color bar
        )
    )

    return fig



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=9000)
