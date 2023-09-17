import cv2
import argparse
import supervision as sv
import torch
import time

from ultralytics import YOLO


def main():
    """
    Annotates a video with object detection bounding boxes and displays real-time FPS.

    This script processes a video using YOLO object detection and annotates it with bounding boxes
    around detected objects. It also displays the real-time frames per second (FPS) of the video.

    Args:
        -i (str): Path to the input video file.
        -o (str): Path to the output video file.
        --live-show (bool, optional): Show the annotation in real-time (default: False).
        -fps (float, optional): Desired frames per second (FPS) for the output video (default: 25.0).
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
    parser.add_argument("-o", type=str, default="video_annotated.mp4",
                        help="Output video file name, will always be in output_files folder")
    parser.add_argument("--live-show", action="store_true",
                        help="Show the annotation in live")
    parser.add_argument("-fps", type=float, default=25.0,
                        help="Desired fps for the output video")
    args = parser.parse_args()

    # Always putting the file in the output folder
    args.o = "output_files/" + args.o

    # Create VideoCapture objects for input and output videos
    cap = cv2.VideoCapture(args.i)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(args.o, fourcc, args.fps, (int(
        cap.get(3)), int(cap.get(4))))  # cap.get(3) returns width

    model = YOLO("yolov8l.pt")

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    prev_end_time = 0
    start_time = 0

    while True:
        start_time = time.time()

        ret, frame = cap.read()

        if not ret:
            break

        result = model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_ultralytics(result)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, _, confidence, class_id, _
            in detections
        ]
        frame = box_annotator.annotate(
            scene=frame,
            detections=detections,
            labels=labels
        )

        # Can't compute it for first frame
        if (prev_end_time > 0 and args.live_show):
            # Calculate the FPS of frame - 1
            fps = 1.0 / elapsed_time

            # Add FPS text to the top-left corner of the frame
            fps_text = f"FPS: {fps:.2f}"
            # Add FPS text to the top-left corner of the frame
            cv2.putText(frame, fps_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        if (args.live_show):
            cv2.imshow("yolov8", frame)

        if cv2.waitKey(30) == 27:
            break

        # Write the frame with bounding boxes to the output video
        out.write(frame)

        prev_end_time = time.time()
        elapsed_time = prev_end_time - start_time

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    global_elapsed_time = time.time() - global_start_time
    print(f"The whole process took {global_elapsed_time} seconds to execute")


if __name__ == "__main__":
    main()
