import argparse
import os
from ultralytics import YOLO


def main():
    """
    Train a YOLO model on a custom dataset of birds using Ultralytics.

    This script trains a YOLO model on a custom dataset of birds. It allows you to specify various training parameters
    such as the data configuration file, project directory, image size, number of epochs, batch size, and experiment name.

    Args:
        -model (str): Model to use (default: 'yolov8m.pt').
        -data (str): Path to the data configuration file (default: 'birds.yaml').
        -project (str): Directory where training runs and results will be saved (default: 'output_training').
        -imgsz (int): Input image size (default: 640).
        -epochs (int): Number of training epochs (default: 15).
        -batch (int): Batch size for training (default: 12).
        -name (str): Name for the experiment and output files (default: 'yolov8_birds').
    """

    # Argument parser for customizing training parameters
    parser = argparse.ArgumentParser(
        description="Train a YOLOv8 model on a custom dataset of birds")
    parser.add_argument("-model", type=str,
                        default="yolov8m.pt", help="Model to use. Comes from ultralytics")
    parser.add_argument("-data", type=str, default="birds.yaml",
                        help="Path to the data configuration file")
    parser.add_argument("-output", type=str, default="train_and_validation",
                        help="Directory for saving training runs and results")
    parser.add_argument("-imgsz", type=int, default=640,
                        help="Input image size")
    parser.add_argument("-epochs", type=int, default=15,
                        help="Number of training epochs")
    parser.add_argument("-batch", type=int, default=12,
                        help="Batch size for training")
    parser.add_argument("-name", type=str, default="yolov8_train",
                        help="Name for the folder containing the results of this train")
    args = parser.parse_args()

    # Create the project directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Initialize the YOLO model
    model = YOLO(args.model)

    # Start training
    model.train(
        data=args.data,
        project=args.output,
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        name=args.name,
        device=0
    )


if __name__ == "__main__":
    main()
