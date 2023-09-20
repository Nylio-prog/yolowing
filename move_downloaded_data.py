import os
import shutil
import argparse

# Function to reorganize the video files


def reorganize_videos(source_folder, destination_folder):
    for root, _, files in os.walk(source_folder):
        for filename in files:
            if filename.endswith(".mp4"):
                parent_folder_name = os.path.basename(root)
                mp4_file_name = parent_folder_name + ".mp4"
                source_path = os.path.join(root, filename)
                destination_path = os.path.join(
                    destination_folder, mp4_file_name)

                # Rename and move the file to the specified folder
                shutil.move(source_path, destination_path)
                print(f"Moved: {source_path} -> {destination_path}")


def main():
    parser = argparse.ArgumentParser(description="Reorganize video files.")
    parser.add_argument(
        "-i", type=str, help="Path to the source folder containing video files.")
    parser.add_argument(
        "-o", type=str, help="Path to the destination folder where video files will be moved.")

    args = parser.parse_args()

    source_folder = args.i
    destination_folder = args.o

    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Call the function to reorganize the video files
    reorganize_videos(source_folder, destination_folder)


if __name__ == "__main__":
    main()
