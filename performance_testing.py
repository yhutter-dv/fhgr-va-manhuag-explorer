import json
import pandas as pd
import time
from preprocessing import calculate_similarity_score 
import plotly.express as px


def get_manga_by_title(mangas, manga_title):
	for manga in mangas:
		if manga["title"] == manga_title:
			return manga
	return None

def measure_performance_get_top_10_similar_mangas(mangas, title):
	reference_manga = get_manga_by_title(mangas, title) 
	similar_mangas = []

	t1 = time.perf_counter(), time.process_time()
	for compare_manga in mangas:
		similar_manga = {
			"id": compare_manga["id"],
			"title": compare_manga["title"],
			"similarity_score":  calculate_similarity_score(reference_manga, compare_manga)
		}
		similar_mangas.append(similar_manga)
	# Only keep top 10 results
	most_similar_mangas = sorted(similar_mangas, key=lambda d: d['similarity_score'], reverse=True)[0:10]
	t2 = time.perf_counter(), time.process_time()
	time_ms = (t2[0] - t1[0]) * 1000
	return time_ms 

def measure_performance_get_top_10_similar_mangas_via_lookup(mangas, title):
	t1 = time.perf_counter(), time.process_time()
	reference_manga = get_manga_by_title(mangas, title) 
	most_similar_mangas = reference_manga["similar_mangas"]

	t2 = time.perf_counter(), time.process_time()
	time_ms = (t2[0] - t1[0]) * 1000
	return time_ms 

if __name__ == "__main__":
	# Read in manga data
	with open("./manga.json", "r", encoding="utf-8") as f:
		manga_data = json.load(f)

	# Read preprocessed data
	with open("./data_preprocessed.json", "r", encoding="utf-8") as f:
		preprocessed_data = json.load(f)

	performance_results = []
	reference_manga_title = "Omniscient Reader (Novel)"

	for scale_factor in range(1, 30, 5):
		mangas = manga_data["mangas"] * scale_factor
		num_elements = len(mangas)
		real_ms = measure_performance_get_top_10_similar_mangas(mangas, reference_manga_title)
		precalculated_ms = measure_performance_get_top_10_similar_mangas_via_lookup(mangas, reference_manga_title)
		real_time_result = {
			"lookup_type": "Real Time",
			"time": real_ms,
			"num_elements": num_elements
		}
		precalculated_time_result = {
			"lookup_type": "Precalculated Time",
			"time": precalculated_ms,
			"num_elements": num_elements
		}
		performance_results.append(real_time_result)
		performance_results.append(precalculated_time_result)

		print(f"Precalculated lookup time is {precalculated_ms}")

	df = pd.DataFrame(performance_results)
	fig = px.bar(df, x="num_elements", y="time", color="lookup_type", title=f"Time to find the 10 most similar mangas to '{reference_manga_title}'", labels={"num_elements": "Number of Mangas", "time": "Time in Milliseconds"})
	fig.write_image("./performance_result.png")


	



