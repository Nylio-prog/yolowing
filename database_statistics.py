import csv
import argparse
import matplotlib.pyplot as plt
import os

# Would be better to average the species count for each species


def find_feeder_with_most_species(species_per_feeder):
    # Initialize variables to keep track of the feeder and species counts
    selected_feeder = None
    min_species_count = float('inf')

    for feeder, data in species_per_feeder.items():
        species_count = data['species_count']

        # Initialize selected_feeder with the first feeder encountered
        if selected_feeder is None:
            selected_feeder = feeder
            min_species_count = species_count
        else:
            # Check if this feeder has more species and fewer counts than the current minimum
            if len(data['species_names']) > len(species_per_feeder[selected_feeder]['species_names']) and species_count < min_species_count:
                selected_feeder = feeder
                min_species_count = species_count

    return selected_feeder


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

   # Create a dictionary to store species per feeder
    species_per_feeder = {}

    # Read the data from the file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            species = row["species"]
            # Assuming "feeder" is the column name in your CSV
            feeder = row["feeder"]

            if feeder not in species_per_feeder:
                species_per_feeder[feeder] = {
                    "species_count": 0, "species_names": [], "species_counts": {}}

            if species != 'NA':
                species_per_feeder[feeder]["species_count"] += 1

                if species not in species_per_feeder[feeder]["species_names"]:
                    species_per_feeder[feeder]["species_names"].append(species)

                if species not in species_per_feeder[feeder]["species_counts"]:
                    species_per_feeder[feeder]["species_counts"][species] = 1
                else:
                    species_per_feeder[feeder]["species_counts"][species] += 1

    # Calculate basic statistics
    total_feeders = len(species_per_feeder)
    unique_species = set(species for data in species_per_feeder.values()
                         for species in data["species_names"])

    # Print basic statistics
    print("Basic Statistics:")
    print(f"Total Feeder: {total_feeders}")
    print(f"Unique Species: {len(unique_species)}")

    # Count occurrences of each species by feeder
    species_counts_by_feeder = {}
    for feeder, data in species_per_feeder.items():
        species_counts_by_feeder[feeder] = data["species_count"]

    for feeder, data in species_per_feeder.items():
        print(f"Feeder: {feeder}")
        print(f"Total of Species Counted: {data['species_count']}")
        print(f"Species Names: {', '.join(data['species_names'])}\n")

        # Print counts of each species for the current feeder
        print("Species Counts:")
        for species, count in data["species_counts"].items():
            print(f"{species}: {count}")

        print()

    # Print species occurrences by feeder
    print("\nSpecies Occurrences by Feeder:")
    for feeder, data in species_per_feeder.items():
        print(f"Feeder: {feeder}")
        for species, count in data["species_counts"].items():
            print(f"{species}: {count} times")
        print()

    # Call the function to find the feeder
    selected_feeder = find_feeder_with_most_species(species_per_feeder)
    print(f"Feeder with the most species and lowest counts: {selected_feeder}")

    # Create a bar chart for species occurrences
    plt.figure(figsize=(10, 6))
    species_counts_by_species = {}
    for data in species_per_feeder.values():
        for species, count in data["species_counts"].items():
            if species in species_counts_by_species:
                species_counts_by_species[species] += count
            else:
                species_counts_by_species[species] = count

    plt.bar(species_counts_by_species.keys(),
            species_counts_by_species.values())
    plt.xlabel("Species")
    plt.ylabel("Occurrences")
    plt.title("Species Occurrences")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the bar chart to the output folder
    chart_filename = os.path.join(output_folder, "species_occurrences.png")
    plt.savefig(chart_filename)

    plt.show()


if __name__ == "__main__":
    main()
