# Manga and Manwha Data Explorer
This is a simple Dashboard written with Python for the `Visual Analytics Module @ FHGR` which explores a `Manga`, `Manwha` Dataset from `Anime Planet`.
The purpose of this Dashboard is to find visual interesting patterns based on `Tags`.

## Prerequisites
- An up to date version of Python (I used `Python Version 3.13.0`)
- An up to date version of Pip (I used `pip Version 24.2`)

## Setup
First it is recommended that you create a `virtual environment` and install all necessary packages.
This can be done by executing the following commands inside your terminal:
```bash
cd src
python3 -m venv .venv
source .venv/bin/activate.sh # UNIX
source .venv/bin/Activate.bat # Windows
pip3 install -r requirements.txt
```

## Preprocessing
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
TODO

## References
- [Dataset](https://www.kaggle.com/datasets/victorsoeiro/manga-manhwa-and-manhua-dataset)
