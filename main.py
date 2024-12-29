from dash import Dash, dcc, html, Input, Output, callback, no_update, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import requests

def load_preprocessed_data():
    with open("./data_preprocessed.json") as f:
        preprocessed_data = json.load(f)
    return preprocessed_data

def load_manga_data():
    with open("./manga.json") as f:
        manga_data = json.load(f)
    return manga_data 

plotly_theme = "plotly_white"

scatter_number_of_mangas_per_tag_id = "scatter-number-of-mangas-per-tag-id"
line_avg_score_for_tags_over_time_id = "line-avg-score-for-tags_over-time-id "
bar_top_ratings_for_tags_id = "bar-top-ratings-for-tags-id "
bar_similar_mangas_id = "bar-similar-mangas-id "
similar_mangas_title_id = "similar-mangas-title-id"

modal_manga_detail_id = "modal-manga-detail-id"
modal_manga_detail_title_id = "modal-manga-detail-title-id"
modal_manga_detail_body_id = "modal-manga-detail-body-id"
modal_manga_detail_loading_spinner_id = "modal-manga-detail-loading-spinner-id"
modal_manga_detail_loading_spinner_content_id = "modal-manga-detail-loading-spinner-content-id"

timerange_slider_id = "time-ranger-slider-id"
tags_dropdown_id = "tags-dropdown-id"

preprocessed_data = load_preprocessed_data()
manga_data = load_manga_data()
tag_descriptions = preprocessed_data["tag_descriptions"]

tags_df = pd.DataFrame(preprocessed_data["tags"])
top_ratings_df = pd.DataFrame(preprocessed_data["top_ratings"])
manga_df = pd.DataFrame(manga_data["mangas"])

years = preprocessed_data["years"]
# Years are already sorted in descending order
max_year = years[0]
min_year = years[-1]
tag_dropdown_options = [{ "label": f"{t['tag_description']} ({t['num_mangas_total']})", "value": t["tag_id"] } for t in tag_descriptions]

def get_manga_from_click_data(click_data):
    first_point = click_data["points"][0]
    manga_id = first_point["customdata"][0]
    manga = manga_df[manga_df["id"] == manga_id]
    return manga

def get_dropdown_value_as_list(dropdown_value):
    # The inital value if one element is selected can be a string such as 'action' instead of a list
    if type(dropdown_value) is list:
        return dropdown_value
    else:
        return [dropdown_value]

@callback(
    Output(component_id=bar_top_ratings_for_tags_id, component_property='figure'),
    Input(component_id=timerange_slider_id, component_property='value'),
    Input(component_id=tags_dropdown_id, component_property='value'),
    Input(component_id=line_avg_score_for_tags_over_time_id, component_property='relayoutData'),
)
def update_bar_top_ratings_for_tags(timerange_slider_value, tags_dropdown_value, tags_over_time_data):
    min_year = timerange_slider_value[0]
    max_year = timerange_slider_value[1]

    # Use min and max year from relayoutData if available
    if tags_over_time_data != None and "xaxis.range[0]" in tags_over_time_data:
        min_year = int(tags_over_time_data["xaxis.range[0]"])
        max_year = int(tags_over_time_data["xaxis.range[1]"])

    tags_to_filter = get_dropdown_value_as_list(tags_dropdown_value)

    # Filter by year and tags
    bar_df = top_ratings_df[(top_ratings_df["year"] >= min_year) & (top_ratings_df["year"] <= max_year) & (top_ratings_df["tag_id"].isin(tags_to_filter))].copy()
    fig = px.bar(bar_df,
        x='year',
        y='rating',
        custom_data='manga_id',
        barmode="group",
        color='tag_id',
        text='title', 
        labels={'rating': 'Manga Rating', 'year': 'Year'},
        template=plotly_theme
    )
    return fig



@callback(
    Output(component_id=scatter_number_of_mangas_per_tag_id, component_property='figure'),
    Input(component_id=timerange_slider_id, component_property='value'),
    Input(component_id=tags_dropdown_id, component_property='value'),
)
def update_scatter_number_of_mangas_per_tag(timerange_slider_value, tags_dropdown_value):
    min_year = timerange_slider_value[0]
    max_year = timerange_slider_value[1]
    tags_to_filter = get_dropdown_value_as_list(tags_dropdown_value)

    # Filter by year and tags
    scatter_df = tags_df[(tags_df["year"] >= min_year) & (tags_df["year"] <= max_year) & (tags_df["tag_id"].isin(tags_to_filter))].copy()
    # Remove any rows where the average rating is NAN
    scatter_df = scatter_df.dropna(subset=['average_rating'])


    # Create bubble size column which is a normalized value based on the average_rating
    # If we did not do that the sizes of each bubble would stay the same if the values of the average ratings are close to each other 
    scatter_df['bubble_size'] = (scatter_df['average_rating'] - scatter_df['average_rating'].min()) / (scatter_df['average_rating'].max() - scatter_df['average_rating'].min()) * 100 
    fig = px.scatter(scatter_df,
        x="year",
        y="number_of_mangas",
        size="bubble_size",
        color="tag_id",
        hover_name="tag_id",
        hover_data={"bubble_size": False}, # Remove bubble size from hover data
        labels={'year': 'Year', 'number_of_mangas': 'Number of Mangas'},
        template=plotly_theme
    )
    return fig

@callback(
    Output(component_id=line_avg_score_for_tags_over_time_id, component_property='figure'),
    Input(component_id=timerange_slider_id, component_property='value'),
    Input(component_id=tags_dropdown_id, component_property='value'),
)
def update_line_avg_score_for_tags_over_time(timerange_slider_value, tags_dropdown_value):
    min_year = timerange_slider_value[0]
    max_year = timerange_slider_value[1]
    tags_to_filter = get_dropdown_value_as_list(tags_dropdown_value)

    # Filter by year and tags
    line_df = tags_df[(tags_df["year"] >= min_year) & (tags_df["year"] <= max_year) & (tags_df["tag_id"].isin(tags_to_filter))].copy()
    # Remove any rows where the average rating is NAN
    line_df = line_df.dropna(subset=['average_rating'])

    fig = px.line(
        line_df,
        x="year",
        y="average_rating",
        color="tag_id",
        labels={'year': 'Year', 'average_rating': 'Average Rating'},
        template=plotly_theme
    )
    return fig 


@callback(
    Output(component_id=similar_mangas_title_id, component_property='children'),
    Output(component_id=bar_similar_mangas_id, component_property='figure'),
    Input(component_id=bar_top_ratings_for_tags_id, component_property='clickData'),
)
def update_bar_similar_mangas(top_results_data):
    if top_results_data == None:
        return no_update

    # Extract the manga_id out of the customdata
    first_point = top_results_data["points"][0]
    manga_id = first_point["customdata"][0]
    manga_title = first_point["text"]
    # Find the matching manga and extract out similar mangas into its own data frame.
    df_similar_mangas = manga_df[manga_df["id"] == manga_id].explode("similar_mangas")
    df_similar_mangas = pd.DataFrame(df_similar_mangas['similar_mangas'].tolist())
    fig = px.bar(
        df_similar_mangas,
        custom_data='id',
        x='title',
        y='similarity_score',
        labels={'title': 'Manga Title', 'similarity_score': 'Similarity Score'},
        template=plotly_theme
    )

    title = f"Liked '{manga_title}' ?"
    return (title, fig)

@callback(
    Output(component_id=modal_manga_detail_id, component_property='is_open'),
    Output(component_id=modal_manga_detail_title_id, component_property='children'),
    Output(component_id=modal_manga_detail_body_id, component_property='children'),
    Input(component_id=bar_similar_mangas_id, component_property='clickData'),
)
def update_manga_detail_modal(click_data):
    if click_data == None:
        return no_update

    manga = get_manga_from_click_data(click_data)
    manga_title = manga["title"].iloc[0]
    manga_description = manga["description"].iloc[0]

    body = html.Div([
        html.H3("Story"),
        html.P(manga_description),
    ])
    return (True, manga_title, body)

@callback(
    Output(component_id=modal_manga_detail_loading_spinner_content_id, component_property='children'),
    Input(component_id=bar_similar_mangas_id, component_property='clickData'),
)
def update_manga_detail_modal_similar_manga_content(click_data):
    if click_data == None:
        return no_update

    manga = get_manga_from_click_data(click_data)
    manga_title = manga["title"].iloc[0]

    # Get recommendations via Jikan REST API
    # See here for more information: https://docs.api.jikan.moe/
    recommendations = get_jikan_manga_recommendations(manga_title)
    recommendation_title = "No recommendations found"
    if len(recommendations) > 0:
        recommendation_title = "You may also like"
    list_elements = []

    # Create list elements for each recommendation
    for recommendation in recommendations:
        title, url = recommendation
        list_element = html.Li(html.A(title, href=url, target='_blank'))
        list_elements.append(list_element)

    return html.Div([
        html.H3(recommendation_title),
        html.Ul(list_elements)
    ])

def prepare_layout():
    header = html.Div([html.H3("Manhuag Explorer", className="text-white fw-bold")], className="p-2 bg-primary")

    modal_dialog = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Header", id=modal_manga_detail_title_id)),
            dbc.ModalBody(html.Div([
                html.Div(id=modal_manga_detail_body_id),
                dcc.Loading(
                    id=modal_manga_detail_loading_spinner_id,
                    children=[html.Div([html.Div(id=modal_manga_detail_loading_spinner_content_id)])],
                    type="default"
                )
            ]))
        ],
        id=modal_manga_detail_id,
        centered=True,
        is_open=False
    )

    tags_dropdown = dcc.Dropdown(
        id=tags_dropdown_id,
        options=tag_dropdown_options,
        value=tag_dropdown_options[0]["value"],
        multi=True, clearable=False
    )

    tags_section = html.Section([
		html.H6("Select Tags you are interested in", className="text-secondary"),
        tags_dropdown
    ], className="py-2")


    timerange_slider = dcc.RangeSlider(min_year, max_year, 1, value=[min_year, max_year], marks=None, tooltip={
        "placement": "bottom",
        "always_visible": True,
    }, id=timerange_slider_id)

    timerange_section = html.Section([
		html.H6("Select a Timerange you are interested in", className="text-secondary"),
        timerange_slider
    ], className="py-2")


    filter_settings = html.Aside([
    	html.H3("Filter Settings", className="text-primary"),
    	tags_section,
    	timerange_section,
   	], id="filter-settings", className="sticky-top p-1")

    graph_style = {
        "height": "25.7vh" # Each graph should take around 25% of the available screen height
    }

    similar_mangas = dbc.Card([
        dbc.CardBody([
            html.H4("Select a Manga", id=similar_mangas_title_id, className="text-primary"),
            html.Div([dcc.Graph(id=bar_similar_mangas_id, style=graph_style)])
        ])
    ])

    top_results_for_tag = dbc.Card([
        dbc.CardBody([
            html.H4("Top Results for Tags", className="text-primary"),
            html.Div([dcc.Graph(id=bar_top_ratings_for_tags_id, style=graph_style)])
        ])
    ])

    average_score_for_tags_over_time = dbc.Card([
        dbc.CardBody([
            html.H4("Average Score for Tags over Time", className="text-primary"),
            html.Div([dcc.Graph(id=line_avg_score_for_tags_over_time_id, style=graph_style)])
        ])
    ])

    number_of_mangas_per_tag = dbc.Card([
        dbc.CardBody([
            html.H4("Number of Mangas per Tag", className="text-primary"),
            html.Div([dcc.Graph(id=scatter_number_of_mangas_per_tag_id, style=graph_style)])
        ])
    ])

    main_content = html.Main([
        html.Div([
            dbc.Row([
                dbc.Col(similar_mangas, md=12)
            ], className="py-1"),
            dbc.Row([
                dbc.Col(top_results_for_tag, md=6),
                dbc.Col(average_score_for_tags_over_time, md=6),
            ], className="py-1"),
            dbc.Row([
                dbc.Col(number_of_mangas_per_tag, md=12)
            ], className="py-1"),
        ])
    ])

    dashboard = html.Div(dbc.Row([
        dbc.Col(filter_settings, md=3),
        dbc.Col(main_content, md=9)
    ]))

    return html.Div([header, dashboard, modal_dialog], className="container-fluid px-0 dbc")


def get_jikan_manga_id(manga_title):
    url = f'https://api.jikan.moe/v4/manga?q={manga_title}&limit=1'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            first_result = data["data"][0]
            id = first_result["mal_id"]
            return (True, id)
        else:
            print(f"No Jikan Id found for title '{manga_title}'")
            return (False, None)
    else:
        print("Request failed")
        return (False, None)

def get_jikan_manga_recommendations(manga_title):
    # TODO: Perhaps do that as a preprocessing step because this can take around a second
    # which would be noticeable when opening a modal dialog...
    success, id = get_jikan_manga_id(manga_title)
    if not success:
        return []

    url = f'https://api.jikan.moe/v4/manga/{id}/recommendations'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            recommendations = [e["entry"] for e in data["data"][:3]] 
            titles = [r["title"] for r in recommendations]
            urls = [r["url"] for r in recommendations]
            return list(zip(titles, urls))
        else:
            print("No recommendations found")
            return []
    else:
        print("Failed to get recommendations")
        return []

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Manhuag Explorer"
app.layout = prepare_layout()
server = app.server

if __name__ == "__main__":
	app.run_server(debug=True)
