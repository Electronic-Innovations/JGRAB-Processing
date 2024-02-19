"""CLI interface for jgrab_processing project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""
import os
import argparse
from datetime import datetime

import polars as pl
from tqdm import tqdm

import base
import jgrab

# https://stackoverflow.com/questions/1724693/find-a-file-in-python
def find_file(name: str, path: str) -> str:
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def datetime_from_filename(filename: str) -> datetime:
    # Splitting the filename into date-time and the rest
    date_time_part, rest = filename.rsplit('-', 1)
    # Replacing underscores with colons to match the time format
    date_time_part = date_time_part.replace("__", " ")
    # Parsing the date and time
    formatted_date_time = datetime.strptime(date_time_part, "%Y-%m-%d %H_%M")
    return formatted_date_time


def file_list(path: str, force: bool = False) -> list[str]:
    # Get a list of all files in the folder with "JGRAB.txt" at the end
    # of the filename
    data_file_list = [os.path.splitext(f)[0] for
                      f in
                      os.listdir(path) if
                      os.path.isfile(os.path.join(path, f)) and
                      f.endswith('JGRAB.txt')]
    chart_file_list = [os.path.splitext(f)[0] for
                       f in
                       os.listdir(path) if
                       os.path.isfile(os.path.join(path, f)) and
                       f.endswith('.png')]

    # List of .txt files that don't have a matching .png yet
    unprocessed_list = (set([f for f in data_file_list]) ^
                        set([f for f in chart_file_list]))

    if force:
        file_list = data_file_list
    else:
        file_list = list(unprocessed_list)

    return [path + '/' + filename + '.txt' for filename in file_list]


def check_equal_length(list_of_lists):
    # Check if the list of lists is not empty
    if not list_of_lists:
        return True  # Empty list is considered to have equal lengths

    # Get the length of the first list
    first_list_length = len(list_of_lists[0])

    # Compare the length of the first list with the
    # lengths of the remaining lists
    return all(len(lst) == first_list_length for lst in list_of_lists[1:])


def process_file(file_path: str, plots: bool = True) -> list[str]:
    data = jgrab.parse_file(file_path)
    # If data isn't right, we should bail out gracefully.
    if len(data[0]) == 0:
        print(file_path)
        raise Exception("Data file was empty")
    if check_equal_length(data) == False:
        for col in data:
            print(len(col))
        raise Exception("Data file contained values of varying length")
    if check_equal_length(data) and len(data[0]) != 0:
        data_frame = base.process_data(data)
        # ['Dc-V','Sph-Unscaled','RphV','Rphl-Unscaled','SphV']
        data_frame = data_frame.with_columns(
            pl.col('Dc-V').mul(0.0250819000819001),
            pl.col('Sph-Unscaled').mul(0.02289),
            pl.col('RphV').mul(0.0250819000819001),
            pl.col('Rphl-Unscaled').mul(0.034335),
            pl.col('SphV').mul(0.0250819000819001),
        )
        sin_params_r = base.fit_sin_wave(
            data_frame.select(pl.col("time", "RphV")))
        sin_params_s = base.fit_sin_wave(
            data_frame.select(pl.col("time", "SphV")))
        if plots:
            base.plot(data_frame, sin_params_r, sin_params_s, file_path)
        r_THD = base.THD_N(data_frame.to_series(5), data_frame.to_series(2))
        r_Irms = base.rms(data_frame.to_series(3))
        s_THD = base.THD_N(data_frame.to_series(5), data_frame.to_series(4))
        s_Irms = base.rms(data_frame.to_series(1))
        filename = os.path.basename(file_path)
        datetime = datetime_from_filename(filename)
        return [datetime.strftime("%Y-%m-%d %H:%M:%S"), 
                filename, 
                "{:.1f}%".format(r_THD) if abs(sin_params_r[0]) > 300 else "0.0%", 
                "{:.1f}%".format(s_THD) if abs(sin_params_s[0]) > 300 else "0.0%",
                "{:.1f}".format(r_Irms),
                "{:.1f}".format(s_Irms),
                "{:.1f}".format(abs(sin_params_r[0])),
                "{:.1f}".format(abs(sin_params_s[0])),
                "{:.1f}".format(sin_params_r[1]),
                "{:.1f}".format(sin_params_s[1])]
    else:
        raise Exception("Data not the right shape")


def main():  # pragma: no cover
    parser = argparse.ArgumentParser()

    # -f FORCE
    parser.add_argument("path", nargs="*")
    parser.add_argument("-f",
                        "--force",
                        action='store_true',
                        help="Process all text files")
    #parser.add_argument("-pl",
    #                    "--plots",
    #                    help="Generate plots")
    args = parser.parse_args()

    # Define the folder path
    print(args.path)
    path = os.path.abspath(args.path[0])
    print(path)

    if os.path.isfile(path):
        process_file(path)
        # base.plot(data, path)
    elif os.path.isdir(path):
        print("Directory Provided")

        statistics_path = os.path.join(path, "statistics.csv")
        with open(statistics_path, 'w') as stats_file:
            stats_file.write("Time, Filename, THD R, THD S, Irms R, Irms S, Vamp R, Vamp S, freq R, freq S\n")
            files = file_list(path, args.force)
            files.sort(reverse=True)
            for file_path in tqdm(files):
                #stats = process_file(file_path, plots=args.plots)
                stats = process_file(file_path, plots=False)
                stats_line = ', '.join(map(str, stats))
                stats_file.write(stats_line + "\n")
    else:
        print("Not a valid path")
