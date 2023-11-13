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
import jgrab
import polars as pl

def file_list(path: str, force: bool = False) -> list[str]:
    # Get a list of all files in the folder with "JGRAB.txt" at the end of the filename
    data_file_list = [os.path.splitext(f)[0] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('JGRAB.txt')]
    chart_file_list = [os.path.splitext(f)[0] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.png')]

    # List of .txt files that don't have a matching .png yet
    unprocessed_list = set([f for f in data_file_list]) ^ set([f for f in chart_file_list])

    if force:
        file_list = data_file_list
    else:
        file_list = unprocessed_list
    
    return [path + filename + '.txt' for filename in file_list]
    

def main():  # pragma: no cover
    parser = argparse.ArgumentParser()

    # -f FORCE 
    parser.add_argument("path",nargs="*")
    parser.add_argument("-f", "--force", action='store_true', help="Process all text files")

    args = parser.parse_args()

    # Define the folder path
    path = args.path[0]
    if os.path.isfile(path):
        data = jgrab.parse_file(path)
        data_frame = base.process_data(data)
        sin_params = base.fit_sin_wave(data_frame.select(pl.col("time","RphV")))
        base.plot(data_frame, sin_params, path)
        # base.plot(data, path)
    elif os.path.isdir(path):
        print("Directory Provided")
        
        files = file_list(path, args.force)
        print(files)
        for file_path in files:
            data = jgrab.parse_file(file_path)
            data_frame = base.process_data(data)
            sin_params = base.fit_sin_wave(data_frame.select(pl.col("time","RphV")))
            base.plot(data_frame, sin_params, path)
    else:
        print("Not a valid path")