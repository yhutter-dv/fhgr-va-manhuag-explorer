from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json

def prepare_layout():
    header = html.Header([html.H1("Manhuag Explorer")])

    tags_section = html.Section([
		html.H4("Select Tags you are interested in", className="section-title")
    ])
    timerange_section = html.Section([
		html.H4("Select a Timerange you are interested in", className="section-title")
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

app = Dash(__name__, external_stylesheets=[])
app.title = "Manhuag Explorer"
app.layout = prepare_layout()
server = app.server

if __name__ == "__main__":
	app.run_server(debug=True)
