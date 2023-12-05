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
from tqdm import tqdm

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

def check_equal_length(list_of_lists):
    # Check if the list of lists is not empty
    if not list_of_lists:
        return True  # Empty list is considered to have equal lengths

    # Get the length of the first list
    first_list_length = len(list_of_lists[0])

    # Compare the length of the first list with the lengths of the remaining lists
    return all(len(lst) == first_list_length for lst in list_of_lists[1:])

def process_file(file_path: str):
    data = jgrab.parse_file(file_path)
    
    if check_equal_length(data) and len(data[0]) != 0: # If data isn't right, we should bail out gracefully.
        data_frame = base.process_data(data)
        # ['Dc-V','Sph-Unscaled','RphV','Rphl-Unscaled','SphV']
        data_frame = data_frame.with_columns(
            pl.col('Dc-V').mul(0.0250819000819001),
            pl.col('Sph-Unscaled').mul(0.02289),
            pl.col('RphV').mul(0.0250819000819001),
            pl.col('Rphl-Unscaled').mul(0.034335),
            pl.col('SphV').mul(0.0250819000819001),
        )
        sin_params_r = base.fit_sin_wave(data_frame.select(pl.col("time","RphV")))
        sin_params_s = base.fit_sin_wave(data_frame.select(pl.col("time","SphV")))
        base.plot(data_frame, sin_params_r, sin_params_s, file_path)

def main():  # pragma: no cover
    parser = argparse.ArgumentParser()

    # -f FORCE 
    parser.add_argument("path",nargs="*")
    parser.add_argument("-f", "--force", action='store_true', help="Process all text files")

    args = parser.parse_args()

    # Define the folder path
    path = args.path[0]
    if os.path.isfile(path):
        process_file(path)
        # base.plot(data, path)
    elif os.path.isdir(path):
        print("Directory Provided")
        
        files = file_list(path, args.force)
        for file_path in tqdm(files):
            process_file(file_path)
    else:
        print("Not a valid path")