import json
import os
import sys
import csv
import pandas as pd

def create_tag_id(tag):
	# Tag Name: My super fancy tag
	# Tag Id: my_super_fancy_tag
	return tag.replace(" ", "_").lower()

def calculate_similarity_score(manga_a, manga_b):
	# Compare the tags if most of them match we consider the manga as similar
	matching_elements = list(set(manga_a["tags"]).intersection(manga_b["tags"])) 
	max_number_of_matching_elements = len(manga_a["tags"])
	number_of_matched_elements = len(matching_elements)

	# Avoid division by zero error
	if number_of_matched_elements == 0:
		return 0

	similarity_percentage = (100 / max_number_of_matching_elements) * number_of_matched_elements
	return similarity_percentage / 100

def main():
	src_data_path = "data.csv" 
	dest_data_path = "data_preprocessed.json" 
	if not os.path.isfile(src_data_path):
		print(f"Error could not find expected data file {src_data_path}!")
		sys.exit(-1)

	# Load file	and clean up data
	preprocessed_data = {
		"tag_descriptions" : [],
		"years": [],
		"tags": []
	}


	mangas = []
	tags = []
	years = []
	print("Starting Preprocessing")
	print("Cleaning up manga data...")
	with open(src_data_path, "r", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		for index, line in enumerate(reader):
			# Only keep mangas with ratings and year
			if line["rating"] == "" or line["year"] == "nan":
				continue

			# Tags is currently a string "['tag1', 'tag2']"
			# We need to convert it into a list (we can simply split by ,)
			tags_str = line["tags"]
			current_tags = tags_str.replace('[', "").replace(']', "").split(',')
			# Replace single quote character and remove any whitespace
			current_tags = [t.strip().replace("'", "") for t in current_tags]


			title = line["title"]
			description = line["description"]
			rating = float(line["rating"])
			cover =  line["cover"]
			year = int(line["year"])
			years.append(year)
			manga_obj = {
				"id": index,
				"title": title,
				"description": description,
				"rating": rating,
				"year": year,
				"cover": cover,
				"tags":  current_tags
			}
			mangas.append(manga_obj)

			# Only add tags which do not exist already
			new_tags = [t for t in current_tags if t not in tags]
			new_tag_descriptions = [{ "tag_id": create_tag_id(t), "tag_description": t } for t in new_tags ]
			tags = tags + new_tags
			preprocessed_data["tag_descriptions"] = preprocessed_data["tag_descriptions"] + new_tag_descriptions

	# Make years unique
	years = list(set(years))
	years.sort(reverse=True)
	preprocessed_data["years"] = years

	preprocessed_data["top_ratings"] = []


	# Initialize dataframe in order to easily calculate some values for each tag such as average score per year etc.
	manga_df = pd.DataFrame.from_dict(mangas)
	print("Precalculating statistical values ...")
	for tag_description in preprocessed_data["tag_descriptions"]:
		current_tag_id = tag_description["tag_id"]
		current_tag = tag_description["tag_description"]
		for year in preprocessed_data["years"]:
			# Filter by year and specific tag
			filtered_df = manga_df[(manga_df["year"] == year)]
			filtered_df = filtered_df[filtered_df["tags"].apply(lambda x: current_tag in x)]
			num_elements = len(filtered_df)
			avg_rating = None 
			if num_elements > 0:
				# Debug Purpose
				# print(f"Searching for Tag {current_tag} for Year {year} and found {num_elements} results")
				avg_rating = filtered_df["rating"].mean()

			tag_data_per_year = {
				"tag_id": current_tag_id,
				"year": year,
				"average_rating" : avg_rating,
				"number_of_mangas": num_elements,
			}

			# Add ids of mangas
			ratings = []
			for index, row in filtered_df.iterrows():
				rating = row["rating"]
				id = row["id"]
				title = row["title"]
				rating = {
					"tag_id": current_tag_id,
					"manga_id": id,
					"rating": rating,
					"title": title,
					"year": year
				}
				ratings.append(rating)

			# Find Top Ratings
			sorted_ratings = sorted(ratings, key=lambda d: d['rating'], reverse=True)
			if (len(sorted_ratings) > 0):
				preprocessed_data["top_ratings"].append(sorted_ratings[0]) 
			preprocessed_data["tags"].append(tag_data_per_year)

	# Calculate similarty rating between mangas
	print("Calculating similarity ratings between mangas (grab a coffee this might take a while) ...")
	for index, manga in enumerate(mangas):
		similar_mangas = []
		# Go trough each manga again and calcualte how similar those are to the current one
		for compare_manga in mangas:
			similar_manga = {
				"id": compare_manga["id"],
				"title": compare_manga["title"],
				"similarity_score":  calculate_similarity_score(manga, compare_manga)
			}
			similar_mangas.append(similar_manga)

		# Only keep top 10 results
		most_similar_mangas = sorted(similar_mangas, key=lambda d: d['similarity_score'], reverse=True)[0:10]
		manga["similar_mangas"] = most_similar_mangas 

	# Save preprocessed data file
	with open(dest_data_path, 'w', encoding='utf-8') as f:
		json.dump(preprocessed_data, f, indent=4)

	# Save cleaned up version of mangas
	manga_data = {
		"mangas": mangas
	}
	cleaned_manga_data_path = "manga.json"
	with open("manga.json", 'w', encoding='utf-8') as f:
		json.dump(manga_data, f, indent=4)
	print(f"Finished processing, generated: {cleaned_manga_data_path} and {dest_data_path}")


if __name__ == "__main__":
    main()
