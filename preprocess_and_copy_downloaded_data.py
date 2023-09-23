import os
import shutil
import argparse
import csv
import random
import json


def create_destination_folder(destination_folder):
    # Delete the entire folder and its contents if it exists
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)

    # Create the empty destination folder
    os.makedirs(destination_folder, exist_ok=True)


def overwrite_classes_yaml(yaml_file, species_selected):
    final_dataset_path = "created_dataset"
    try:
        # Get the absolute path of yaml_file_path
        absolute_path = os.path.abspath(final_dataset_path)

        # Format the YAML data with the specified requirements
        yaml_data = f"path: {absolute_path}\n"
        yaml_data += f"train: images/train\n"
        yaml_data += f"val: images/val\n"
        yaml_data += f"test: images/test\n"
        yaml_data += f"names:\n"
        for i, species in enumerate(species_selected):
            yaml_data += f"  {i}: {species}\n"
        # Write the formatted YAML data to the file with UTF-8 encoding
        with open(yaml_file, 'w', encoding='utf-8') as yaml_file:
            yaml_file.write(yaml_data)

        print("YAML file updated successfully.")

    except Exception as e:
        print(f"Error while updating YAML file: {str(e)}")


def overwrite_classes_utils(utils_file_path, species_selected):
    try:
        species_list = ', '.join(
            [f'"{species}"' for species in species_selected])
        with open(utils_file_path, 'w', encoding="utf-8") as utils_file:
            utils_file.write(f'SPECIES_LIST = [{species_list}]')

        print("Utils file updated successfully.")

    except Exception as e:
        print(f"Error while updating utils file: {str(e)}")


# Need to improve by randomly taking the max_video_ids_per_species videos instead of sequentially do it
# Also need to regroup the other low occurences species into another one for negative sampling but will require to change the classes in birds.yaml and utils.py
def read_species_data(input_file, yaml_file, utils_file):
    species_counts = {}  # Dictionary to store species counts
    # Dictionary to store video_id as key and species as value for >= 300 occurrences
    species_dict = {}
    occurences_threshold = 200

    print("Counting number of occurences for each species in the database file ...")

    # Count the occurrences of each species in the input file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            video_id = row["video_id"]
            species = row["species"]

            # We don't count 'NA' species and Pas d'oiseau because we can't create a box for them
            if species != 'NA' and species != "Pas d'oiseau":
                species_counts[species] = species_counts.get(species, 0) + 1

    print("Creating species dictionary with balanced species")

    # Populate species_dict with video_id as key and species as value
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            video_id = row["video_id"]
            species = row["species"]
            feeder = row["feeder"]

            # Check if the species count is below the threshold
            if species != 'NA' and species != "Pas d'oiseau":
                if species_counts[species] < occurences_threshold:
                    if feeder == "poecile" or feeder == "fringilla":
                        species_dict[video_id] = {
                            "species": "Autre", "test": "True"}
                    else:
                        species_dict[video_id] = {
                            "species": "Autre", "test": "False"}
                    species_counts["Autre"] = species_counts.get(
                        "Autre", 0) + 1
                else:
                    # TODO: Check smarter for which feeder to pick up from database statistics and specifically \
                    # chose a balanced number for each class
                    # Check if "feeder" is "poecile" or "fringilla" and add "test" dimension accordingly
                    if feeder == "poecile" or feeder == "fringilla":
                        species_dict[video_id] = {
                            "species": species, "test": "True"}
                    else:
                        species_dict[video_id] = {
                            "species": species, "test": "False"}

    # Determine the maximum number of video_ids to keep for each species
    # max_video_ids_per_species = min(
    #     count for count in species_counts.values() if count >= occurences_threshold
    # )

    max_video_ids_per_species = 200

    print(
        f"Maximum amount of videos taken for each species : {max_video_ids_per_species}")
    # Filter species_dict based on species counts and limit to max_video_ids_per_species
    filtered_species_dict = {}
    # Dictionary to keep track of the number of video_ids per species, doesn't include test videos
    video_ids_per_species = {}
    # Dictionary for number of species by each feeder
    species_count_test = {}
    max_count_species_test = 5
    for video_id, data in species_dict.items():
        if species_counts[data["species"]] >= occurences_threshold:
            if data["species"] not in video_ids_per_species:
                video_ids_per_species[data["species"]] = 0

            # If it's a test video, doesn't go through random process and we want to put max_count_species_test videos max
            if data["test"] == "True":
                if data["species"] in species_count_test:
                    if species_count_test[data["species"]] < max_count_species_test:
                        species_count_test[data["species"]] += 1
                        filtered_species_dict[video_id] = {
                            "species": data["species"], "test": data["test"]}
                else:
                    # If "species" key doesn't exist, set it to 1
                    species_count_test[data["species"]] = 1
                    filtered_species_dict[video_id] = {
                        "species": data["species"], "test": data["test"]}

            else:
                # Calculate the probability of including this video based on the current count
                # 2 times the probability to almost ensure that in total there will be max_video_ids_per_species
                # but with better distribution
                probability = 2 * max_video_ids_per_species / \
                    (species_counts[data["species"]] + 1)

                # Randomly decide whether to include this video based on probability
                include_video = random.random() < probability and \
                    video_ids_per_species[data["species"]
                                          ] < max_video_ids_per_species
                if include_video:
                    filtered_species_dict[video_id] = {
                        "species": data["species"], "test": data["test"]}
                    video_ids_per_species[data["species"]] += 1

    # Print information about the filtering process
    total_species = len(species_counts)
    total_filtered_species = len(video_ids_per_species)
    total_filtered_video_ids = len(filtered_species_dict)
    print(f"Total species: {total_species}")
    print(
        f"Species with at least {occurences_threshold} occurrences: {total_filtered_species}")
    print(f"Total filtered video IDs: {total_filtered_video_ids}")

    species_selected = []

    # Print occurrences selected for each species
    for species, count in species_counts.items():
        if species in video_ids_per_species:
            selected_count = video_ids_per_species[species]
            print(
                f"Species: {species}, Occurrences Selected: {selected_count}")
            species_selected.append(species)

    # Print test species selected
    print(f"Testing videos selected:")
    for species, count in species_count_test.items():
        print(f"Species: {species}, Occurences selected: {count}")

    overwrite_classes_yaml(yaml_file, species_selected)
    overwrite_classes_utils(utils_file, species_selected)

    # Specify the file path where you want to save the dictionary
    species_dict_path = 'filtered_species_dict.json'

    # Serialize and save the dictionary to a JSON file
    with open(species_dict_path, 'w', encoding="utf-8") as file:
        json.dump(filtered_species_dict, file)

    return filtered_species_dict


def copy_videos(source_folder, destination_folder, species_dict):
    for root, _, files in os.walk(source_folder):
        for filename in files:
            if filename.endswith(".mp4"):
                parent_folder_name = os.path.basename(root)
                mp4_file_name = parent_folder_name + ".mp4"
                source_path = os.path.join(root, filename)

                # Check if the video is in species_dict before copying
                if parent_folder_name in species_dict:
                    destination_path = os.path.join(
                        destination_folder, mp4_file_name)
                    # Copy the file to the specified folder
                    shutil.copy2(source_path, destination_path)
                    print(f"Copied: {source_path} -> {destination_path}")


def reorganize_and_preprocess_videos(source_folder, destination_folder, input_file, yaml_file, utils_file):
    create_destination_folder(destination_folder)
    species_dict = read_species_data(
        input_file, yaml_file, utils_file)
    copy_videos(source_folder, destination_folder, species_dict)
    print("Preprocessed and copied videos successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Reorganize video files, copy them, and preprocess based on a CSV file.")
    parser.add_argument("-i", type=str, default="videos",
                        help="Path to the input videos folder.")
    parser.add_argument("-o", type=str, default="preprocessed_videos",
                        help="Path to the output destination folder.")
    parser.add_argument("-y", type=str, default="birds.yaml",
                        help="Path to the yaml file.")
    parser.add_argument("-u", type=str, default="utils.py",
                        help="Path to the utils.py file which contains the list of species.")
    parser.add_argument("--db-file", type=str,
                        default="db_export.txt", help="Database to read from the species")
    args = parser.parse_args()

    reorganize_and_preprocess_videos(
        args.i, args.o, args.db_file, args.y, args.u)


if __name__ == "__main__":
    main()
