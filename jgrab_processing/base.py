import sys
import os
from os import listdir
from os.path import isfile, join, splitext
import matplotlib.pyplot as plt
import math
from scipy import optimize
import numpy as np
from tqdm import tqdm, trange
import polars as pl

def rms(numbers):
    # Check for an empty list to avoid division by zero
    if len(numbers) == 0:
        return None

    # Calculate the sum of the squares of the numbers
    sum_of_squares = sum(x ** 2 for x in numbers)

    # Calculate the mean of the squares
    mean_of_squares = sum_of_squares / len(numbers)

    # Take the square root to get the RMS
    rms = math.sqrt(mean_of_squares)

    return rms

def formatNumbers(numbers):
    return ["{:.2f}".format(number) for number in numbers]

def sin_wave(x, amplitude, frequency, phase):
    a = frequency * x
    b = a + phase
    c = np.sin(b)
    d = amplitude * c
    return d
    #return amplitude * np.sin((frequency * x) + phase)

def THD_N(x_values, y_values):
    params, params_covariance = optimize.curve_fit(sin_wave, x_values, y_values, p0=[12000, 0.1, 1])
    fundamental = sin_wave(x_values, params[0], params[1], params[2])
    noise = y_values - fundamental
    return (rms(noise) / rms(fundamental) * 100)

def THD_data(data: list[list[int]]) -> list[float]:
    THD_Values = [THD_N(x_values, data[0]), THD_N(x_values, data[1]), THD_N(x_values, data[2]), THD_N(x_values, data[3]), THD_N(x_values, data[4])]
    return THD_Values

def process_data(data: list[list[int]]) -> pl.dataframe:
    frame = pl.DataFrame(data)
    labels = ['Dc-V','Sph-Unscaled','RphV','Rphl-Unscaled','SphV']
    frame.columns = labels
    
    x_values = [(20 * value / 64) for value in range(len(data[0]))]
    
    frame = frame.with_columns(
        pl.Series(name="time", values=x_values)
    )
    return frame

def fit_sin_wave(data: pl.dataframe) -> list[float]:
    params, params_covariance = optimize.curve_fit(sin_wave, data.to_series(0), data.to_series(1))
    return params

def plot(data: pl.dataframe, sin_wave: list[float], filename: str):
    plt.figure(figsize=(6, 4))
    # plt.scatter(x_data, y_data, label='Data')
    plot_x_start = 0
    plot_x_finish = (20 * 240) / 64
    full_x_values = np.arange(plot_x_start, plot_x_finish, 0.1)
    phase_angle = 0 if sin_wave[0] > 0 else math.pi
    
    a = (sin_wave[1] * full_x_values) + sin_wave[2] # phase_angle
    b = np.sin(a)
    c = sin_wave[0] * b
    sin_wave_values = c
    # sin_wave_values = sin_wave(full_x_values, sin_wave(0), sin_wave(1), phase_angle)
    plt.plot(full_x_values, sin_wave_values,label='Fitted function', color='#D3D3D3')
        
    for i in range(5):
        plt.plot(data.to_series(5), data.to_series(i)) # , label=labels[i])
 
    # Customize the plot
    plt.title(os.path.basename(filename))
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.xlim(plot_x_start, plot_x_finish)
    plt.ylim(-20000, 20000)
    output_filename = os.path.splitext(filename)[0] + ".png"  # Change the filename and format as needed
    plt.savefig(output_filename, format="png")

def main():
    arg = sys.argv[1]
    data = jgrab.parse_file(arg)
    plot(data, arg)

if __name__ == "__main__":
    main()
