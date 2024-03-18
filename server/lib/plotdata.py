import csv
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys
import numpy as np  # Import numpy for array operations


def plot_csv_data(filename):
    x_values = []
    y_values = []
    
    with open(filename, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            x_values.append(float(row[0]))  # First value in each row as x
            y_values.append(float(row[1]))  # Second value in each row as y
    
    # Original dimensions
    original_width, original_height = 1920, -1080
    # Target dimensions
    target_width, target_height = 3000, 2000

    # Calculate scale factors
    x_scale = target_width / original_width
    y_scale = target_height / original_height

    # Apply scaling to data points
    scaled_x_values = [x * x_scale for x in x_values]
    scaled_y_values = [y * y_scale+target_height for y in y_values]
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Scatter plot with inverted Y-axis and scaled Y-values
    ax.scatter(scaled_x_values, scaled_y_values, color='blue', marker='o')
    ax.set_ylim(0, target_height)  # Set Y-axis limits from 0 to target_height
    ax.set_xlim(0, target_width)   # Set X-axis limits from 0 to target_width

    # Add grid
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)  # Add grid with dashed lines

    # Customize grid spacing (10x6)
    xticks = np.linspace(0, target_width, 11)
    yticks = np.linspace(0, target_height, 7)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    # Set axis labels and title
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_title('Launcher Accuracy Three Target Points')

    # Show plot
    plt.show()



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    plot_csv_data(filename)
