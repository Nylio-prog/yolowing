import argparse

from ultralytics import YOLO


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", type=str, default="best_weights/best.pt",
                        help="Model to use")
    args = parser.parse_args()

    # Load the model
    model = YOLO(args.m)

    # Start tuning hyperparameters for model training on the birds dataset
    result_grid = model.tune(data='birds.yaml', epochs=1, iterations=10)


if __name__ == "__main__":
    main()
