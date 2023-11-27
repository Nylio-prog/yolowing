import argparse
import os
from tqdm import tqdm
import shutil
import json


def main():
    """
    Creates a dataset to train a YOLOv8 model for bird detection.

    This script processes a set of input videos and generates an annotated dataset for training a YOLOv8
    model for bird detection. It iterates through the input videos, annotates each of them into one frame with the specified bird species,
    and divides each frame into train and validation sets based on a given probability.

    Args:
        -i (str): Input folder where preprocessed videos are located.
        -o (str): Output folder where annotated frames will be stored.
        --db-file(str): Database to read from the species.
        -p (float): Probability of a video to be in the train set (1 - p probability for validation).

    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="Create a dataset to train a YOLOv8 model for bird detection")
    parser.add_argument("-i", type=str,
                        default="preprocessed_videos", help="Input folder where preprocessed videos are contained")
    parser.add_argument("-o", type=str,
                        default="created_dataset", help="Output folder where frames will be stored")
    parser.add_argument("--json-file", type=str,
                        default="filtered_species_dict.json", help="Json to read from the species, created by preprocess_and_copy_downloaded_data")
    parser.add_argument("-p",  type=float, default=0.8,
                        help="Probability of being in the train folder. 1-p probability of being in validation folder")

    args = parser.parse_args()

    list_videos_path = [os.path.join(root, filename)
                        for root, _, files in os.walk(args.i)
                        for filename in files if filename.endswith(".mp4")]

    print("Reading the json dictionary file ...")

    # Initialize an empty dictionary
    species_dict = {}

    # Read data from the JSON file and store it in the dictionary
    with open(args.json_file, 'r', encoding="utf-8") as file:
        species_dict = json.load(file)

    print(f"{len(list_videos_path)} in total")

    # Delete the entire folder and its contents if it exists
    if os.path.exists(args.o):
        shutil.rmtree(args.o)
        print(f"Deleted existing {args.o} folder")

    print("Creating dataset ...")

    # Iterate over list_videos_path
    for number_video, video_path in tqdm(enumerate(list_videos_path), total=len(list_videos_path)):
        print(video_path)
        try:
            # We don't need the name of the folder where videos are stored
            local_path = video_path.split('/')[1:]
            print(local_path)
            print(species_dict)

            # Define the arguments to pass
            script_command = [
                "python",  # Command to run Python
                "create_annotated_video.py",  # Name of your script
                "-i", video_path,  # Video path
                "-o", args.o,  # Output folder
                # Actual species to annotate
                "-s", f'"{species_dict[local_path]["species"]}"',
                "-n", str(number_video),  # Number of the video
                "-p", str(args.p),  # Probability of being in the train set
            ]

            # Conditionally add the -t argument if it's True
            if species_dict[local_path]["test"] == "True":
                script_command.extend(["-t"])

            # Execute the combined command using os.system
            full_command = " ".join(script_command)
            return_code = os.system(full_command)

            if return_code != 0:
                print(
                    f"Error encountered while processing {video_path}. Skipping...")

            if return_code == 2:
                raise KeyboardInterrupt

        except KeyboardInterrupt:
            print("Process interrupted. Exiting...")
            break

    print(f"Created dataset at {args.o}")


if __name__ == "__main__":
    main()
