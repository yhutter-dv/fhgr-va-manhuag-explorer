from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json

def prepare_layout(tag_dropdown_options, min_year, max_year):
    header = html.Header([html.H1("Manhuag Explorer")])

    initial_tag_dropdown_value = tag_dropdown_options[0]["value"]

    tags_dropdown = dcc.Dropdown(
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
    })

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
        html.Div([], className="chart-container"),
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

def load_preprocessed_data():
    with open("./data_preprocessed.json") as f:
        preprocessed_data = json.load(f)
    return preprocessed_data

preprocessed_data = load_preprocessed_data()
tag_descriptions = preprocessed_data["tag_descriptions"]
years = preprocessed_data["years"]
# Years are already sorted in descending order
max_year = years[0]
min_year = years[-1]
tag_dropdown_options = [{ "label": t["tag_description"], "value": t["tag_id"] } for t in tag_descriptions]

app = Dash(__name__, external_stylesheets=[])
app.title = "Manhuag Explorer"
app.layout = prepare_layout(tag_dropdown_options, min_year, max_year)
server = app.server

if __name__ == "__main__":
	app.run_server(debug=True)
