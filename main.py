import cv2
import argparse
from ultralytics import YOLO
import supervision as sv
import torch
import time

def main():
    # Check if CUDA (GPU support) is available
    use_gpu = torch.cuda.is_available()
    
    if use_gpu:
        device_name = torch.cuda.get_device_name(0)
        print(f"GPU Device: {device_name}")
    else:
        print("No GPU detected. Using CPU.")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-path", type=str, default="video.mp4", help="Path to the input video file")
    args = parser.parse_args()

    # Open the video file for reading
    cap = cv2.VideoCapture(args.video_path)

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

        #Can't compute it for first frame
        if (prev_end_time > 0):
            # Calculate the FPS of frame - 1
            fps = 1.0 / elapsed_time

            # Add FPS text to the top-left corner of the frame
            fps_text = f"FPS: {fps:.2f}"
            # Add FPS text to the top-left corner of the frame
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow("yolov8", frame)

        if cv2.waitKey(30) == 27:
            break

        prev_end_time = time.time()
        elapsed_time = prev_end_time - start_time


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
