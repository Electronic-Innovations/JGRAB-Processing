"""CLI interface for jgrab_processing project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""
import os
import argparse
import subprocess

import base

def main():  # pragma: no cover
    parser = argparse.ArgumentParser()

    # -f FORCE 
    parser.add_argument("folder",nargs="*")
    parser.add_argument("-f", "--force", action='store_true', help="Process all text files")

    args = parser.parse_args()

    # Define the folder path
    folder_path = args.folder[0]

    # Define the Python script to run for each file
    script_to_run = 'parseFile.py'

    # Get a list of all files in the folder with "JGRAB.txt" at the end of the filename
    data_file_list = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('JGRAB.txt')]
    chart_file_list = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.png')]

    # List of .txt files that don't have a matching .png yet
    unprocessed_list = set([f for f in data_file_list]) ^ set([f for f in chart_file_list])

    if args.force:
        file_list = data_file_list
    else:
        file_list = unprocessed_list

    print("Processing ", len(file_list), " files")

    # Iterate through the list of files and run the script for each file
    for filename in file_list:
        # Pass the filename to the script_to_run.py as an argument
        withExtension = filename + '.txt'
        script_command = ['python', script_to_run, withExtension]

        # Run the script using subprocess
        subprocess.run(script_command, cwd=folder_path)