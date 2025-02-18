# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

unique_launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in unique_launch_sites]

range_slider_marks = {i: str(i) for i in range(0, 10001, 1000)}

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div(
                                    dcc.Dropdown(
                                    id='site-dropdown',
                                    value='ALL',
                                    options=dropdown_options,
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                    )
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                html.Div(
                                    dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        marks=range_slider_marks,
                                        value=[0, 10000]
                                    )
                                ),
                                
                                #dcc.RangeSlider(id='payload-slider',...)

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output


@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Group by Launch Site and calculate success rate
        site_success_rate = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
        site_success_rate.columns = ['Launch Site', 'Success Rate']
        site_success_rate['Success Rate'] *= 100  # Convert to percentage

        # Create pie chart for success rate per site
        fig = px.pie(site_success_rate, values='Success Rate', names='Launch Site', 
                     title='Success Rate per Launch Site',
                     labels={'Success Rate': 'Success Rate (%)'},
                     color_discrete_sequence=px.colors.qualitative.Set2)

    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Count occurrences of class values (1 = success, 0 = failure)
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']

        # Create pie chart for the selected site's success vs failure
        fig = px.pie(class_counts, values='count', names='class', 
                     title=f'Success vs Failure for {entered_site}',
                     labels={'class': 'Mission Outcome'},
                     color_discrete_map={1: 'green', 0: 'red'})  # Green for success, red for failure

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [
                Input(component_id='site-dropdown', component_property='value'),
                Input(component_id='payload-slider', component_property='value')
              ])
def update_success_payload_scatter(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) & 
                              (filtered_df['Payload Mass (kg)'] <= max_payload)]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',  # 1 = Success, 0 = Failure
        color='Booster Version Category',
        title=f'Success Rate by Payload Mass for {selected_site}',
        labels={'class': 'Mission Outcome'},
        symbol='class',  # Different symbols for success/failure
        size_max=10
    )

    return fig                              



# Run the app
if __name__ == '__main__':
    app.run_server()
