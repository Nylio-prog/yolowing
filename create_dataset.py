import argparse
import os
from tqdm import tqdm
import csv


def main():
    """
    Creates a dataset to train a YOLOv8 model for bird detection.

    This script processes a set of input videos and generates an annotated dataset for training a YOLOv8
    model for bird detection. It iterates through the input videos, annotates each of them into one frame with the specified bird species,
    and divides each frame into train and validation sets based on a given probability.

    Args:
        -i (str): Input folder where videos are located.
        -o (str): Output folder where annotated frames will be stored.
        --db-file(str): Database to read from the species.
        -p (float): Probability of a video to be in the train set (1 - p probability for validation).

    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="Create a dataset to train a YOLOv8 model for bird detection")
    parser.add_argument("-i", type=str,
                        default="input_files", help="Input folder where videos are contained")
    parser.add_argument("-o", type=str,
                        default="created_dataset", help="Output folder where frames will be stored")
    parser.add_argument("--db-file", type=str,
                        default="db_export.txt", help="Database to read from the species")
    parser.add_argument("-p",  type=float, default=0.8,
                        help="Probability of being in the train folder. 1-p probability of being in validation folder")

    args = parser.parse_args()

    list_videos_path = [os.path.join(args.i, filename)
                        for filename in os.listdir(args.i)]

    # Define the input file name
    input_file = args.db_file

    # Create a dictionary to store the species data
    species_dict = {}

    print("Reading the database file ...")

    # Read the data from the file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            video_id = row["video_id"]
            species = row["species"]

            # We don't add to the dict if it's NA
            if species != 'NA':
                species_dict[video_id] = species

    # Filter list_videos_path based on species_dict
    valid_list_videos_path = [
        video_path for video_path in list_videos_path
        if os.path.splitext(os.path.basename(video_path))[0] in species_dict
    ]

    print(f"{len(valid_list_videos_path)} videos were annotated out of {len(list_videos_path)} in total")

    print("Creating dataset ...")

    # Iterate over valid_list_videos_path
    for number_video, video_path in tqdm(enumerate(valid_list_videos_path), total=len(valid_list_videos_path)):

        video_id = os.path.splitext(os.path.basename(video_path))[0]

        # Not all videos are annotated but we don't want to create
        # dataset without annotation so we skip the for loop
        if (video_id not in species_dict):
            continue

        # Define the arguments to pass
        script_command = [
            "python",  # Command to run Python
            "create_annotated_video.py",  # Name of your script
            "-i", video_path,  # Video path
            "-o", args.o,  # Output folder
            "-s", f'"{species_dict[video_id]}"',  # Actual species to annotate
            "-n", str(number_video),  # Number of the video
            "-p", str(args.p)  # Probability of being in train set
        ]

        # Execute the combined command using os.system
        full_command = " ".join(script_command)
        os.system(full_command)


if __name__ == "__main__":
    main()
