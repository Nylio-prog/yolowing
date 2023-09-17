import cv2
import argparse
import supervision as sv
import torch
import time
import os

from ultralytics import YOLO
from utils import SPECIES_LIST


def create_directories(image_dir, label_dir):
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)


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
        -i (str): Path to the input video file.
        -s (str): Name of species to annotate for each boxes on every frames.
    """

    global_start_time = time.time()

    # Check if CUDA (GPU support) is available
    use_gpu = torch.cuda.is_available()

    if use_gpu:
        device_name = torch.cuda.get_device_name(0)
        print(f"GPU Device: {device_name}")
    else:
        print("No GPU detected. Using CPU.")

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, default="input_files/video.mp4",
                        help="Path to the input video file")
    parser.add_argument("-s",  type=str, choices=SPECIES_LIST,
                        help="Annotate every animal boxes with this parameter. Must be in the list of species")
    args = parser.parse_args()

    # Create VideoCapture objects for input and output videos
    cap = cv2.VideoCapture(args.i)

    # Get the width and height of the video frames
    image_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    image_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    model = YOLO("yolov8l.pt")

    for key in range(14, 25):
        model.names[key] = 'bird'

    image_dir = "created_dataset/images/train"
    label_dir = "created_dataset/labels/train"

    create_directories(image_dir, label_dir)

    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        result = model(frame, agnostic_nms=True)[0]
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

            # Generate a timestamp-based unique identifier
            timestamp = int(time.time())  # Using seconds
            frame_id = f"{frame_count:04}"

            # Combine the timestamp and frame_id to create a 12-character identifier
            unique_id = f"{timestamp:08}{frame_id}"

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
    print(f"The whole process took {global_elapsed_time} seconds to execute")


if __name__ == "__main__":
    main()
