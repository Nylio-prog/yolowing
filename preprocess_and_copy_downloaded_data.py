import os
import shutil
import argparse
import csv
import numpy as np
import json
from collections import defaultdict


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


def count_species_occurrences(input_file, occurences_threshold):
    species_counts = defaultdict(int)

    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        all_rows = list(reader)

    for row in all_rows:
        species = row["species"]
        if species != 'NA' and species != "Pas d'oiseau":
            species_counts[species] += 1

    # Identify species below the occurrences threshold
    species_to_modify = [species for species, count in species_counts.items(
    ) if count < occurences_threshold]

    # Modify species below the occurrences threshold to "Autre"
    for species in species_to_modify:
        species_counts["Autre"] += species_counts[species]
        del species_counts[species]

    return species_counts


def get_unique_years(input_file):
    unique_years = set()

    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            year = int(row["date"].split("-")[0])
            unique_years.add(year)

    return sorted(list(unique_years))


def create_species_dict(input_file, species_counts, occurences_threshold, max_local_paths_per_species_per_year):
    species_dict = {}
    max_local_paths_per_species_per_year = 50
    max_count_species_test = 30

    # Read all rows from the input file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        all_rows = list(reader)

    # Create a dictionary to store all rows for each species
    rows_per_species = defaultdict(list)
    for row in all_rows:
        species = row["species"]
        if species_counts[species] >= occurences_threshold or species == "Autre":
            rows_per_species[species].append(row)

    # Get unique years from the database
    years = get_unique_years(input_file)

    # Calculate evenly spaced indices for local paths for each species and each year
    for species, rows in rows_per_species.items():
        for year in years:
            year_rows = [
                row for row in rows if row["date"].split("-")[0] == str(year)]
            total_species_occurrences_per_year = len(year_rows)

            # Skip the year if there are no species for that year
            if total_species_occurrences_per_year == 0:
                continue

            # Determine the appropriate max value based on the year
            if year == "2021":
                max_value = max_count_species_test
            else:
                max_value = max_local_paths_per_species_per_year

            # Calculate evenly spaced indices based on the determined max value
            evenly_spaced_indices = np.linspace(
                0, total_species_occurrences_per_year - 1, max_value, dtype=int)
            np.random.shuffle(evenly_spaced_indices)

            for index in evenly_spaced_indices:
                row = year_rows[index]
                local_path = row["local_path"]

                # Set "test" based on the year
                if year == "2021":
                    species_dict[local_path] = {
                        "species": species, "test": "True"}
                else:
                    species_dict[local_path] = {
                        "species": species, "test": "False"}

    return species_dict


def print_species_info(species_counts, species_dict, occurences_threshold):
    total_species = len(species_counts)
    species_selected = [entry["species"] for entry in species_dict.values()]

    result_str = f"Total species: {total_species}\n"
    result_str += f"Species with at least {occurences_threshold} occurrences: {len(species_selected)}\n"
    result_str += f"Total video : {len(species_dict.keys())}\n"

    # Print occurrences selected for each species
    for species, count in species_counts.items():
        if species in species_selected:
            count_species_occurrences = sum(1 for entry in species_dict.values(
            ) if entry["species"] == species and entry["test"] == "False")
            result_str += f"Species: {species}, Occurrences Selected: {count_species_occurrences}\n"

    # Print test species selected
    result_str += "Testing videos selected:\n"
    for species, count in species_counts.items():
        if species in species_selected:
            count_species_occurrences = sum(1 for entry in species_dict.values(
            ) if entry["species"] == species and entry["test"] == "True")
            result_str += f"Species: {species}, Occurrences selected: {count}\n"

    # Print to console
    print(result_str)

    # Save to file
    with open("preprocessing_log.txt", mode="w", encoding="utf-8") as log_file:
        log_file.write(result_str)


def read_species_data(input_file, yaml_file, utils_file):
    occurences_threshold = 200
    max_local_paths_per_species_per_year = 200
    species_counts = count_species_occurrences(
        input_file, occurences_threshold)

    print("Creating species dictionary with balanced species")

    species_dict = create_species_dict(
        input_file, species_counts, occurences_threshold, max_local_paths_per_species_per_year)

    print(
        f"Maximum amount of videos taken for each species per year: {max_local_paths_per_species_per_year}")

    print_species_info(species_counts,
                       species_dict, occurences_threshold)

    species_selected = [entry["species"] for entry in species_dict.values()]

    overwrite_classes_yaml(yaml_file, species_selected)
    overwrite_classes_utils(utils_file, species_selected)

    species_dict_path = 'filtered_species_dict.json'

    with open(species_dict_path, 'w', encoding="utf-8") as file:
        json.dump(species_dict, file)

    return species_dict


def copy_videos(source_folder, destination_folder, species_dict):
    # Check if the video is in species_dict before copying
    for video in species_dict.keys():
        # In the db_file it's written .h264 instead of .mp4 as the actual filename
        mp4_video_path = video.replace(".h264", ".mp4")
        destination_path = os.path.join(
            destination_folder, mp4_video_path)

        full_mp4_video_path = os.path.join(source_folder, mp4_video_path)
        # Copy the file to the specified folder
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.copy2(full_mp4_video_path, destination_path)

        print(f"Copied: {full_mp4_video_path} -> {destination_path}")


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
                        default="db_file.tsv", help="Database to read from the species")
    args = parser.parse_args()

    reorganize_and_preprocess_videos(
        args.i, args.o, args.db_file, args.y, args.u)


if __name__ == "__main__":
    main()
