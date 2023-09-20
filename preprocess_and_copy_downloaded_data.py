import os
import shutil
import argparse
import csv

def create_destination_folder(destination_folder):
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

#Need to improve by randomly taking the max_video_ids_per_species videos instead of sequentially do it
#Also need to regroup the other low occurences species into another one for negative sampling but will require to change the classes in birds.yaml and utils.py
def read_species_data(input_file):
    species_counts = {}  # Dictionary to store species counts
    species_dict = {}   # Dictionary to store video_id as key and species as value for >= 300 occurrences
    occurences_threshold = 300

    # Count the occurrences of each species in the input file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            video_id = row["video_id"]
            species = row["species"]

            # We don't count 'NA' species
            if species != 'NA':
                species_counts[species] = species_counts.get(species, 0) + 1

            # Populate species_dict with video_id as key and species as value
            species_dict[video_id] = species

    # Determine the maximum number of video_ids to keep for each species
    max_video_ids_per_species = min(
        count for count in species_counts.values() if count >= occurences_threshold
    )

    print(f"Maximum amount of videos taken for each species : {max_video_ids_per_species}")

    # Filter species_dict based on species counts and limit to max_video_ids_per_species
    filtered_species_dict = {}
    video_ids_per_species = {}  # Dictionary to keep track of the number of video_ids per species
    for video_id, species in species_dict.items():
        if species_counts[species] >= occurences_threshold:
            if species not in video_ids_per_species:
                video_ids_per_species[species] = 0
            if video_ids_per_species[species] < max_video_ids_per_species:
                filtered_species_dict[video_id] = species
                video_ids_per_species[species] += 1

    # Print information about the filtering process
    total_species = len(species_counts)
    total_filtered_species = len(video_ids_per_species)
    total_filtered_video_ids = len(filtered_species_dict)
    print(f"Total species: {total_species}")
    print(f"Species with at least {occurences_threshold} occurrences: {total_filtered_species}")
    print(f"Total filtered video IDs: {total_filtered_video_ids}")

    # Print occurrences selected for each species
    for species, count in species_counts.items():
        if species in video_ids_per_species:
            selected_count = video_ids_per_species[species]
            print(f"Species: {species}, Occurrences Selected: {selected_count}")

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

def reorganize_and_preprocess_videos(source_folder, destination_folder, input_file):
    create_destination_folder(destination_folder)
    species_dict = read_species_data(input_file)
    copy_videos(source_folder, destination_folder, species_dict)
    print("Preprocessed and copied videos successfully!")

def main():
    parser = argparse.ArgumentParser(description="Reorganize video files, copy them, and preprocess based on a CSV file.")
    parser.add_argument("-i", type=str, default="videos", help="Path to the input CSV file.")
    parser.add_argument("-o", type=str, default="preprocessed_videos", help="Path to the output destination folder.")
    parser.add_argument("--db-file", type=str,
                        default="db_export.txt", help="Database to read from the species")
    args = parser.parse_args()

    reorganize_and_preprocess_videos(args.i, args.o, args.db_file)

if __name__ == "__main__":
    main()
