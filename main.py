import cv2
import argparse
import torch
import time

from ultralytics import YOLO
from collections import Counter


def most_common_value(arr):
    counter = Counter(arr)
    most_common = counter.most_common(1)

    if most_common:
        return most_common[0][0]
    else:
        return None


def main():
    """
    Annotates a video with object detection bounding boxes and displays real-time FPS.

    This script processes a video using YOLO object detection and annotates it with bounding boxes
    around detected objects. It also displays the real-time frames per second (FPS) of the video.

    Args:
        -i (str): Path to the input video file.
        -o (str): Path to the output video file.
        --not-show (bool, optional): Show the annotation in real-time (default: False).
        -save (bool): Save to a video file
        -fps (float, optional): Desired frames per second (FPS) for the output video (default: 25.0).
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, default="input_files/video.mp4",
                        help="Path to the input video file")
    parser.add_argument("-o", type=str, default="video_annotated.mp4",
                        help="Output video file name, will always be in output_files folder")
    parser.add_argument("-m", type=str, default="best_weights/best.pt",
                        help="Model to use")
    parser.add_argument("--not-show", action="store_true", default=False,
                        help="Show the annotation in not")
    parser.add_argument("-save", action="store_true",
                        help="Show the annotation in not")
    parser.add_argument("-fps", type=float, default=25.0,
                        help="Desired fps for the output video")
    args = parser.parse_args()

    global_start_time = time.time()

    # Check if CUDA (GPU support) is available
    use_gpu = torch.cuda.is_available()

    if use_gpu:
        device_name = torch.cuda.get_device_name(0)
        print(f"GPU Device: {device_name}")
    else:
        print("No GPU detected. Using CPU.")

    # Always putting the file in the output folder
    args.o = "output_files/" + args.o

    # Create VideoCapture objects for input and output videos
    cap = cv2.VideoCapture(args.i)

    if (args.save):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(args.o, fourcc, args.fps, (int(
            cap.get(3)), int(cap.get(4))))  # cap.get(3) returns width

    model = YOLO(args.m)
    names = model.names
    predicted_labels = []

    prev_end_time = 0
    start_time = 0

    while True:
        start_time = time.time()

        ret, frame = cap.read()

        if not ret:
            break

        result = model(frame, agnostic_nms=True, conf=0.7)[0]
        # Visualize the results on the frame
        annotated_frame = result.plot(
            pil=True, line_width=5, font_size=40)

        if result.boxes.cls.numel() == 0:
            predicted_labels.append(None)
        else:
            for c in result.boxes.cls:
                predicted_labels.append(names[int(c)])

        # Can't compute it for first frame
        if (prev_end_time > 0 and not (args.not_show) and not ((args.save))):
            # Calculate the FPS of frame - 1
            fps = 1.0 / elapsed_time

            # Add FPS text to the top-left corner of the frame
            fps_text = f"FPS: {fps:.2f}"
            # Add FPS text to the top-left corner of the frame
            annotated_frame = annotated_frame.copy()

            cv2.putText(annotated_frame, fps_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

        if (not (args.not_show)):
            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)

        if cv2.waitKey(30) == 27:
            break

        if (args.save):
            # Write the frame with bounding boxes to the output video
            out.write(annotated_frame)

        prev_end_time = time.time()
        elapsed_time = prev_end_time - start_time

    cap.release()
    if (args.save):
        out.release()
    cv2.destroyAllWindows()

    global_elapsed_time = time.time() - global_start_time
    print(f"The whole process took {global_elapsed_time} seconds to execute")

    print(
        f"The most likely bird to be present is {most_common_value(predicted_labels) if most_common_value(predicted_labels) is not None else 'We cannot conclude which species are present in this video.'}")


if __name__ == "__main__":
    main()
