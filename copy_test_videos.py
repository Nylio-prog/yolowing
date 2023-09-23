import os
import shutil
import json


def copy_videos(source_folder, destination_folder, species_dict):
    for root, _, files in os.walk(source_folder):
        for filename in files:
            if filename.endswith(".mp4"):
                parent_folder_name = os.path.basename(root)
                mp4_file_name = parent_folder_name + ".mp4"
                source_path = os.path.join(root, filename)

                # Check if the video is in species_dict before copying
                if parent_folder_name in species_dict and species_dict[parent_folder_name]["test"] == "True":
                    destination_path = os.path.join(
                        destination_folder, mp4_file_name)
                    # Copy the file to the specified folder
                    shutil.copy2(source_path, destination_path)
                    print(f"Copied: {source_path} -> {destination_path}")


def main():
    source_folder = "videos"
    destination_folder = "test_videos"

    # Read species_dict from a JSON file
    with open("filtered_species_dict.json", "r") as json_file:
        species_dict = json.load(json_file)

    copy_videos(source_folder, destination_folder, species_dict)


if __name__ == "__main__":
    main()
