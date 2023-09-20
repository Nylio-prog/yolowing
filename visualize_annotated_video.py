import cv2
import argparse
import os
import numpy as np

from PIL import Image, ImageDraw, ImageFont
from utils import SPECIES_LIST


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, default="created_dataset/images/train",
                        help="Path to the directory containing images")
    parser.add_argument("-l", type=str, default="created_dataset/labels/train",
                        help="Path to the directory containing label files")
    args = parser.parse_args()

    image_files = os.listdir(args.i)
    label_files = os.listdir(args.l)

    for image_file in image_files:
        image_path = os.path.join(args.i, image_file)
        label_file = os.path.join(args.l, image_file.replace(".jpg", ".txt"))

        if os.path.exists(label_file):
            image = cv2.imread(image_path)
            height, width, _ = image.shape  # Get image dimensions

            with open(label_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            font = ImageFont.truetype("arial.ttf", 30)

            for line in lines:
                parts = line.strip().split(" ")
                class_id = int(parts[0])
                center_x, center_y, width_normalized, height_normalized = map(
                    float, parts[1:5])

                # Calculate bounding box coordinates
                half_width = width_normalized * width / 2
                half_height = height_normalized * height / 2

                x1 = int((center_x * width) - half_width)
                y1 = int((center_y * height) - half_height)
                x2 = int((center_x * width) + half_width)
                y2 = int((center_y * height) + half_height)

                # Convert class_id to class name using SPECIES_LIST
                class_name = SPECIES_LIST[class_id]

                # Calculate the text size and position
                text = f"{class_name}"
                text_size = draw.textbbox(
                    (x1, y1), text, font=font, anchor="lb")

                text_x = text_size[0]
                text_y = text_size[1] - 2

                # Draw the rectangle with background color
                rect_color = (170, 0, 0)  # Green color for the rectangle
                draw.rectangle(text_size, fill=rect_color)

                # Draw a bounding box on the image
                box_color = (170, 0, 0)  # Green color for the bounding box
                thickness = 4
                draw.rectangle([x1, y1, x2, y2],
                               outline=box_color, width=thickness)

                # Add class name as text with UTF-8 encoding
                text_color = (0, 0, 0)  # White color for text
                draw.text((text_x, text_y), text, font=font, fill=text_color)

            # Convert the Pillow image back to OpenCV format for display
            image_with_text = cv2.cvtColor(
                np.array(pil_image), cv2.COLOR_RGB2BGR)

            # Display the image with bounding boxes and handle key events
            cv2.imshow("Image with Bounding Boxes", image_with_text)

            # Wait for a key press for a specified duration (in milliseconds)
            # If the 'Escape' key (27) is pressed, break the loop and close the window
            key = cv2.waitKey(0) & 0xFF
            if key == 27:
                break

    # Close all OpenCV windows when done
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
