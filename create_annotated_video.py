import cv2
import argparse
import supervision as sv
import torch
import time
import os
import random

from ultralytics import YOLO
from tqdm import tqdm
from utils import SPECIES_LIST


def create_images_labels_directories(images_train_dir, images_val_dir, labels_train_dir, labels_val_dir):

    os.makedirs(images_train_dir, exist_ok=True)
    os.makedirs(images_val_dir, exist_ok=True)
    os.makedirs(labels_train_dir, exist_ok=True)
    os.makedirs(labels_val_dir, exist_ok=True)


def create_bird_annotation(class_id, x1, y1, x2, y2, width, height):
    # Normalize coordinates
    x1_normalized = x1 / width
    y1_normalized = y1 / height
    x2_normalized = x2 / width
    y2_normalized = y2 / height

    bird_annotation = f"{class_id} {x1_normalized:.6f} {y1_normalized:.6f} {x2_normalized:.6f} {y2_normalized:.6f}\n"
    return bird_annotation


def save_image(image_path, frame):
    cv2.imwrite(image_path, frame)


def save_label(label_path, bird_annotation):
    with open(label_path, 'w') as label_file:
        label_file.write(bird_annotation)


def main():
    """
    Creates a part of the dataset with images and labels by using pretrained model and merging every animals into birds and giving which bird species it is.

    Args:
        -i (str): Path to the input video file (default="input_files/video.mp4").
        -o (str): Path to the input video file (default="created_dataset").
        -s (str): Name of species to annotate for each boxes on every frames.
        -n (int): Number of the video (default=0).
        -p (float): Probability of being in the train folder (default=0.8).
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, default="input_files/video.mp4",
                        help="Path to the input video file")
    parser.add_argument("-o", type=str, default="created_dataset",
                        help="Path to the output video file")
    parser.add_argument("-s",  type=str, choices=SPECIES_LIST,
                        help="Annotate every animal boxes with this parameter. Must be in the list of species")
    parser.add_argument("-n",  type=int, default=0,
                        help="Number of the video. Used to name the output")
    parser.add_argument("-p",  type=float, default=0.8,
                        help="Probability of being in the train folder. 1-p probability of being in validation folder")
    args = parser.parse_args()

    global_start_time = time.time()

    # Check if CUDA (GPU support) is available
    use_gpu = torch.cuda.is_available()

    if use_gpu:
        device_name = torch.cuda.get_device_name(0)
        print(f"GPU Device: {device_name}")
    else:
        print("No GPU detected. Using CPU.")

    # Create VideoCapture objects for input and output videos
    cap = cv2.VideoCapture(args.i)

    # Get the width and height of the video frames
    image_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    image_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    model = YOLO("yolov8l.pt")

    for key in range(14, 25):
        model.names[key] = 'bird'

    images_train_dir = os.path.join(args.o, "images/train")
    images_val_dir = os.path.join(args.o, "images/val")
    labels_train_dir = os.path.join(args.o, "labels/train")
    labels_val_dir = os.path.join(args.o, "labels/val")

    # Split every frame on the video into train or validation folder to avoid the model to learn the video and just recognize from which video the frame is from
    if random.random() < args.p:
        print("Will be in the train folder")
        image_dir = images_train_dir
        label_dir = labels_train_dir
    else:
        print("Will be in the validation folder")
        image_dir = images_val_dir
        label_dir = labels_val_dir

    create_images_labels_directories(
        images_train_dir, images_val_dir, labels_train_dir, labels_val_dir)

    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        result = model(frame, agnostic_nms=True, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(result)
        labels = [
            f"{model.model.names[class_id]}"
            for _, _, _, class_id, _
            in detections
        ]

        for label in labels:
            if (label != "bird"):
                break

            x1, y1, x2, y2 = detections[0].xyxy[0][:4]

            class_id = SPECIES_LIST.index(args.s)

            frame_id = f"{frame_count:04}"

            # Combine the timestamp and frame_id to create a 12-character identifier
            unique_id = f"{args.n:08}{frame_id}"

            # Create image and label paths with the unique identifier
            image_path = os.path.join(image_dir, f"{unique_id}.jpg")
            label_path = os.path.join(label_dir, f"{unique_id}.txt")

            # Save the image and label with the unique identifier
            save_image(image_path, frame)
            save_label(label_path, create_bird_annotation(
                class_id, x1, y1, x2, y2, image_width, image_height))

            frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    global_elapsed_time = time.time() - global_start_time
    print(
        f"The process of this video took {global_elapsed_time} seconds to execute")


if __name__ == "__main__":
    main()