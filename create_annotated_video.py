import cv2
import argparse
import supervision as sv
import os
import random

from ultralytics import YOLO
from utils import SPECIES_LIST


def create_images_labels_directories(images_train_dir, images_val_dir, images_test_dir, labels_train_dir, labels_val_dir, labels_test_dir):

    os.makedirs(images_train_dir, exist_ok=True)
    os.makedirs(images_val_dir, exist_ok=True)
    os.makedirs(images_test_dir, exist_ok=True)
    os.makedirs(labels_train_dir, exist_ok=True)
    os.makedirs(labels_val_dir, exist_ok=True)
    os.makedirs(labels_test_dir, exist_ok=True)


def create_bird_annotation(class_id, x1, y1, x2, y2, width, height):
    # Calculate center, width, and height normalized values
    center_x_normalized = ((x1 + x2) / 2) / width
    center_y_normalized = ((y1 + y2) / 2) / height
    width_normalized = (x2 - x1) / width
    height_normalized = (y2 - y1) / height

    # This is the dataset format that is required by YOLOv8
    bird_annotation = f"{class_id} {center_x_normalized:.6f} {center_y_normalized:.6f} {width_normalized:.6f} {height_normalized:.6f}\n"
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
        -t (bool): If specified, the data will be in the test set.
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
    parser.add_argument("-t", action="store_true", default=False,
                        help="If specified, the data will be in the test set.")

    args = parser.parse_args()

    # Create VideoCapture objects for input and output videos
    cap = cv2.VideoCapture(args.i)

    # Get the width and height of the video frames
    image_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    image_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    model_downloaded = False

    model_name = "yolov8m.pt"

    if os.path.exists(model_name):
        model_downloaded = True

    model = YOLO(model_name)

    if not (model_downloaded):
        print("Model downloaded")

    for key in range(14, 25):
        model.names[key] = 'bird'

    images_train_dir = os.path.join(args.o, "images/train")
    images_val_dir = os.path.join(args.o, "images/val")
    images_test_dir = os.path.join(args.o, "images/test")
    labels_train_dir = os.path.join(args.o, "labels/train")
    labels_val_dir = os.path.join(args.o, "labels/val")
    labels_test_dir = os.path.join(args.o, "labels/test")

    # Split every frame on the video into train, validation, or test folder
    if (args.t):
        image_dir = images_test_dir
        label_dir = labels_test_dir
    else:
        probability = random.random()
        if probability < args.p:
            image_dir = images_train_dir
            label_dir = labels_train_dir
        else:
            image_dir = images_val_dir
            label_dir = labels_val_dir

    create_images_labels_directories(
        images_train_dir, images_val_dir, images_test_dir, labels_train_dir, labels_val_dir, labels_test_dir)

    frame_count = 0

    while True:
        ret, frame = cap.read()
        print("frame count : " + str(frame_count))

        if not ret:
            break

        # Since we have many frames in one video, instead of learning on similar images, we take one frame every 3 frames.
        print("bool = " + str(frame_count % 3 != 0))
        if frame_count % 3 != 0:
            frame_count += 1
            continue

        result = model(frame, agnostic_nms=True, verbose=False, device=0)[0]
        detections = sv.Detections.from_ultralytics(result)
        labels = [
            f"{model.model.names[class_id]}"
            for _, _, _, class_id, _
            in detections
        ]

        # We only want to detect one bird in the image as there could be multiple but the species given is only one.
        # This could possibly select the wrong bird's species if there are 2 and the first label is the wrong bird's species.
        already_found_bird = False
        for label in labels:
            if (label != "bird" or already_found_bird):
                break

            already_found_bird = True

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
            print("image saved")

        frame_count += 1

    cap.release()


if __name__ == "__main__":
    main()
