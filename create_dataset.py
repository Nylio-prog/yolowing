import subprocess
import argparse
import os
from tqdm import tqdm


def main():
    """
    Creates a dataset to train a YOLOv8 model for bird detection.

    This script processes a set of input videos and generates an annotated dataset for training a YOLOv8
    model for bird detection. It iterates through the input videos, annotates each of them into one frame with the specified bird species,
    and divides each frame into train and validation sets based on a given probability.

    Args:
        -i (str): Input folder where videos are located.
        -o (str): Output folder where annotated frames will be stored.
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
    parser.add_argument("-p",  type=float, default=0.8,
                        help="Probability of being in the train folder. 1-p probability of being in validation folder")

    args = parser.parse_args()

    list_videos_path = os.listdir(args.i)

    print("Creating dataset ...")

    for number_video, video_path in tqdm(enumerate(list_videos_path), total=len(list_videos_path)):

        # Retrieve the species annotated by members of the assocation
        species = "perruche à collier"

        # Define the arguments to pass
        command = [
            "python",  # Command to run Python
            "create_annotated_video.py",  # Name of your script
            "-i", video_path,  # Video path
            "-o", args.o,  # Output folder
            "-s", species,  # Actual species to annotate
            "-n", number_video,  # Number of the video
            "-p", args.p  # Probability of being in train set
        ]

        print(command)

        # Execute the script with the specified arguments
        # subprocess.run(command)


if __name__ == "__main__":
    main()
