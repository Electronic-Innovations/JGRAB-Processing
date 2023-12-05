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
    a = 2 * math.pi * frequency * x
    b = a + phase
    c = np.sin(b)
    d = amplitude * c
    return d
    #return amplitude * np.sin((frequency * x) + phase)

def THD_N(x_values, y_values):
    params, params_covariance = optimize.curve_fit(sin_wave, x_values, y_values, p0=[350.0, 50.0, 0.0])
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
    
    x_values = [(0.02 * value / 64) for value in range(len(data[0]))]
    
    frame = frame.with_columns(
        pl.Series(name="time", values=x_values)
    )
    
    out = frame.select(
        pl.col('Dc-V').cast(pl.Float64),
        pl.col('Sph-Unscaled').cast(pl.Float64),
        pl.col('RphV').cast(pl.Float64),
        pl.col('Rphl-Unscaled').cast(pl.Float64),
        pl.col('SphV').cast(pl.Float64),
        pl.col('time'),
    )
    
    return out

def fit_sin_wave(data: pl.dataframe) -> list[float]:
    params, params_covariance = optimize.curve_fit(sin_wave, data.to_series(0), data.to_series(1), [350.0, 50.0, 0.0])
    #print(params_covariance)
    
    return params

def plot(data: pl.dataframe, sin_wave_params_r: list[float], sin_wave_params_s: list[float], filename: str):
    #plt.figure(figsize=(6, 4))
    fig, axs = plt.subplots(3, 1, figsize=(16, 10))
    # plt.scatter(x_data, y_data, label='Data')
    plot_x_start = 0
    plot_x_finish = (127 * 0.02) / 64
    full_x_values = np.arange(plot_x_start, plot_x_finish, 0.0001)
    phase_angle = 0 if sin_wave_params_r[0] > 0 else math.pi
    
    #a = (sin_wave[1] * full_x_values) + sin_wave[2] # phase_angle
    #b = np.sin(a)
    #c = sin_wave[0] * b
    #sin_wave_values = c
    sin_wave_values_r = sin_wave(full_x_values, sin_wave_params_r[0], sin_wave_params_r[1], sin_wave_params_r[2])
    axs[0].plot(full_x_values, sin_wave_values_r, label='Fitted function', color='#D3D3D3')
    
    sin_wave_values_s = sin_wave(full_x_values, sin_wave_params_s[0], sin_wave_params_s[1], sin_wave_params_s[2])
    axs[0].plot(full_x_values, sin_wave_values_s, label='Fitted function s', color='#D3D3D3')
    # x_values = [(x - (sin_wave_params[2] / (2 * math.pi * sin_wave_params[1]))) for x in data.to_series(5)]
    
    axs[0].plot(data.to_series(5), data.to_series(2))
    r_THD = THD_N(data.to_series(5), data.to_series(2))
    
    axs[0].plot(data.to_series(5), data.to_series(4))
    s_THD = THD_N(data.to_series(5), data.to_series(4))
     
    # Customize the plot
    axs[0].set_title(os.path.basename(filename))
    #axs[0].xlabel("Time")
    #axs[0].ylabel("Voltage")
    axs[0].set_xlim(plot_x_start, plot_x_finish)
    axs[0].set_ylim(-400, 400)
    axs[0].set_ylabel("Voltage (VAC)")
    axs[0].annotate("R THD+N {:.1f}%".format(r_THD), xy=(0, 360))
    axs[0].annotate("S THD+N {:.1f}%".format(s_THD), xy=(0, 320))
    axs[0].grid(True, linewidth = 0.2, alpha = 0.4)
    
    
    axs[1].plot(data.to_series(5), data.to_series(3))
    axs[1].plot(data.to_series(5), data.to_series(1))
    axs[1].set_xlim(plot_x_start, plot_x_finish)
    axs[1].set_ylim(-85, 85)
    axs[1].set_ylabel("Current (A)")
    axs[1].grid(True, linewidth = 0.2, alpha = 0.4)
    
    axs[2].plot(data.to_series(5), data.to_series(0))
    axs[2].set_xlim(plot_x_start, plot_x_finish)
    axs[2].set_ylim(-10, 850)
    axs[2].set_ylabel("Voltage (VDC)")
    axs[2].set_xlabel("Time (sec)")
    axs[2].grid(True, linewidth = 0.2, alpha = 0.4)
    
    plt.tight_layout()
    output_filename = os.path.splitext(filename)[0] + ".png"  # Change the filename and format as needed
    plt.savefig(output_filename, format="png")
    plt.close()

def main():
    arg = sys.argv[1]
    data = jgrab.parse_file(arg)
    plot(data, arg)

if __name__ == "__main__":
    main()
