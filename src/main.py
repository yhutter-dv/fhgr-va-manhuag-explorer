from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd
import json

def load_preprocessed_data():
    with open("./data_preprocessed.json") as f:
        preprocessed_data = json.load(f)
    return preprocessed_data

scatter_number_of_mangas_per_tag_id = "scatter-number-of-mangas-per-tag-id"
timerange_slider_id = "time-ranger-slider-id"
tags_dropdown_id = "tags-dropdown-id"

preprocessed_data = load_preprocessed_data()
tag_descriptions = preprocessed_data["tag_descriptions"]
tags_df = pd.DataFrame(preprocessed_data["tags"])
years = preprocessed_data["years"]
# Years are already sorted in descending order
max_year = years[0]
min_year = years[-1]
tag_dropdown_options = [{ "label": t["tag_description"], "value": t["tag_id"] } for t in tag_descriptions]

def calc_marker_size_safe(row):
    min_size = 0.1
    if pd.isna(row["average_rating"]):
        return min_size
    return (row["average_rating"] / 10.0) + min_size

@callback(
    Output(component_id=scatter_number_of_mangas_per_tag_id, component_property='figure'),
    Input(component_id=timerange_slider_id, component_property='value'),
    Input(component_id=tags_dropdown_id, component_property='value'),
)
def update_scatter_number_of_mangas_per_tag(timerange_slider_value, tags_dropdown_value):
    min_year = timerange_slider_value[0]
    max_year = timerange_slider_value[1]
    tags_to_filter = []
    # The inital value if no element is selected can be a string such as 'action' instead of a list
    # God knows why...
    if type(tags_dropdown_value) is list:
        tags_to_filter = tags_dropdown_value
    else:
        tags_to_filter = [tags_dropdown_value]

    # Filter by year and tags
    scatter_df = tags_df[(tags_df["year"] >= min_year) & (tags_df["year"] <= max_year) & (tags_df["tag_id"].isin(tags_to_filter))].copy()
    scatter_df["marker_size"] = scatter_df.apply(calc_marker_size_safe, axis=1)
    hover_data = { "marker_size": False }
    fig = px.scatter(scatter_df,
        x="year",
        y="number_of_mangas",
        size="marker_size",
        color="tag_id",
        hover_name="tag_id",
        hover_data=hover_data
    )
    return fig

def prepare_layout():
    header = html.Header([html.H1("Manhuag Explorer")])

    initial_tag_dropdown_value = tag_dropdown_options[0]["value"]

    tags_dropdown = dcc.Dropdown(
        id=tags_dropdown_id,
        options=tag_dropdown_options,
        value=initial_tag_dropdown_value,
        multi=True, clearable=False
    )

    tags_section = html.Section([
		html.H4("Select Tags you are interested in", className="section-title"),
        tags_dropdown
    ])

    tooltip_style = {
        "color": "var(--foreground)",
        "backgroundColor": "var(--background)",
    } 

    timerange_slider = dcc.RangeSlider(min_year, max_year, 1, value=[min_year, max_year], marks=None, tooltip={
        "placement": "bottom",
        "always_visible": True,
        "style": tooltip_style,
    }, id=timerange_slider_id)

    timerange_section = html.Section([
		html.H4("Select a Timerange you are interested in", className="section-title"),
        timerange_slider
    ])

    spacer = html.Div([], className="spacer")

    filter_settings = html.Aside([
    	html.H3("Filter Settings", className="title"),
    	tags_section,
    	timerange_section,
   	], id="filter-settings")

    similar_mangas = html.Div([
        html.H4("Liked Solo Leveling?", className="title yellow"),
        html.Div([], className="chart-container")
    ], className="card", id="similar-mangas")


    top_results_for_tag = html.Div([
        html.H4("Top 5 Results for Tag asdf", className="title yellow"),
        html.Div([], className="chart-container")
    ], className="card")

    average_score_for_tags_over_time = html.Div([
        html.H4("Average Score for Tags over Time", className="title yellow"),
        html.Div([], className="chart-container")
    ], className="card")

    number_of_mangas_per_tag = html.Div([
        html.H4("Number of Mangas per Tag", className="title yellow"),
        html.Div([dcc.Graph(id=scatter_number_of_mangas_per_tag_id)], className="chart-container"),
    ], className="card", id="number-of-mangas-per-tag")

    main_content = html.Main([
        html.Div([
            similar_mangas,
            top_results_for_tag,
            average_score_for_tags_over_time,
            number_of_mangas_per_tag
        ], className="grid")
    ], id="content")
    dashboard = html.Div([filter_settings, main_content], id="dashboard")
    return html.Div([header, dashboard], className="wrapper")


app = Dash(__name__, external_stylesheets=[])
app.title = "Manhuag Explorer"
app.layout = prepare_layout()
server = app.server

if __name__ == "__main__":
	app.run_server(debug=True)
