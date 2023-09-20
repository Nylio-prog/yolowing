import csv
import argparse
import matplotlib.pyplot as plt
import os


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Process a file and create a species dictionary.")
    parser.add_argument("--db-file", type=str,
                        default="db_export.txt", help="Input file name")
    parser.add_argument("--output-folder", type=str,
                        default="statistics", help="Output folder for graphs")

    # Parse command line arguments
    args = parser.parse_args()

    # Define the input file name
    input_file = args.db_file

    # Create the output folder if it doesn't exist
    output_folder = args.output_folder
    os.makedirs(output_folder, exist_ok=True)

    # Create a dictionary to store the species data
    species_dict = {}

    # Read the data from the file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            video_id = row["video_id"]
            species = row["species"]

            # We don't add to the dict if it's NA
            if species != 'NA':
                species_dict[video_id] = species

    # Calculate basic statistics
    total_entries = len(species_dict)
    unique_species = list(set(species_dict.values()))

    # Print basic statistics
    print("Basic Statistics:")
    print(f"Total Entries: {total_entries}")
    print(f"Unique Species: {len(unique_species)}")

    # Count occurrences of each species
    species_counts = {species: list(species_dict.values()).count(
        species) for species in unique_species}

    # Print species occurrences
    print("\nSpecies Occurrences:")
    for species, count in species_counts.items():
        print(f"{species}: {count} times")

    # Create a bar chart for species occurrences
    plt.figure(figsize=(10, 6))
    plt.bar(species_counts.keys(), species_counts.values())
    plt.xlabel("Species")
    plt.ylabel("Occurrences")
    plt.title("Species Occurrences")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the bar chart to the output folder
    chart_filename = os.path.join(output_folder, "species_occurrences.png")
    plt.savefig(chart_filename)

    # Display the bar chart
    plt.show()


if __name__ == "__main__":
    main()
