# Manga and Manwha Data Explorer (Manhuag Explorer)
This is a simple Dashboard written with Python for the `Visual Analytics Module @ FHGR` which explores a `Manga`, `Manwha` Dataset from `Anime Planet`.
The purpose of this Dashboard is to find visual interesting patterns based on `Tags`.

## Prerequisites
- An up to date version of Python (I used `Python Version 3.13.0`)
- An up to date version of Pip (I used `pip Version 24.2`)

## Setup
First it is recommended that you create a `virtual environment` and install all necessary packages.
This can be done by executing the following commands inside your terminal:
```bash
python3 -m venv .venv
source .venv/bin/activate.sh # UNIX
source .venv/bin/Activate.bat # Windows
pip3 install -r requirements.txt
```

## Preprocessing
> :warning: This produces the files `manga.json` and `data_preprocessed.json`. These files should aready exist. Therefore you do not need to run this script again. If you do it takes quite a while.

In order to preprocess the data a small Python Script named `preprocessing.py` was written. 
```bash
python3 preprocessing.py 
```

## Running the Application
In order to run the Application execute the following command
```bash
python3 main.py
```
## See it in Action
You can see it online [here](https://fhgr-va-manhuag-explorer-229692aab0ff.herokuapp.com/)

## References
- [Dataset](https://www.kaggle.com/datasets/victorsoeiro/manga-manhwa-and-manhua-dataset)
- [Jikan REST API](https://jikan.moe/)
- [How to deploy to Heroku](https://towardsdatascience.com/deploying-your-dash-app-to-heroku-the-magical-guide-39bd6a0c586c)
- [Style Dash Components](https://hellodash.pythonanywhere.com/adding-themes/dcc-components)
- [Plotly Themes](https://plotly.com/python/templates/)