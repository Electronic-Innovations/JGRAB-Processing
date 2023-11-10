import sys
import os
from os import listdir
from os.path import isfile, join, splitext
import matplotlib.pyplot as plt
import math
from scipy import optimize
import numpy as np
from tqdm import tqdm, trange

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
    return amplitude * np.sin((frequency * x)+phase)

def THD_N(x_values, y_values):
    params, params_covariance = optimize.curve_fit(sin_wave, x_values, y_values, p0=[12000, 0.1, 1])
    fundamental = sin_wave(x_values, params[0], params[1], params[2])
    noise = y_values - fundamental
    return (rms(noise) / rms(fundamental) * 100)


def plot(data: list[list[int]], filename: str):
    # Create x-axis values (e.g., for the time points)
    x_values = range(len(data[0]))  # Assuming the x-axis represents time or index

    labels = ['Dc-V','Sph-Unscaled','RphV','Rphl-Unscaled','SphV']

    max_values = [max(values) for values in data]
    min_values = [min(values) for values in data]
    rms_values = [rms(values) for values in data]
    # print(max_values)
    # print(min_values)
    # print(formatNumbers(rms_values))

    # Attempt to fit a sin wave to each waveform

    parameters = []

    for i in range(len(data)):
        params, params_covariance = optimize.curve_fit(sin_wave, x_values, data[i], p0=[12000, 0.1, 1])
        parameters.append(params)

    # print(parameters)

    
    THD_Values = [THD_N(x_values, data[0]), THD_N(x_values, data[1]), THD_N(x_values, data[2]), THD_N(x_values, data[3]), THD_N(x_values, data[4])]
    # print(THD_N(x_values, data[0]))
    # print(THD_N(x_values, data[1]))
    # print(THD_N(x_values, data[2]))
    # print(THD_N(x_values, data[3]))
    # print(THD_N(x_values, data[4]))


    # Plot each column of data
    #for i in range(len(data)):
    #    plt.plot(x_values, data[i], label=f'Column {i + 1}')
    # print(60 * params[2])
    # print([(x + (60 * params[2])) for x in x_values])

    params, params_covariance = optimize.curve_fit(sin_wave, x_values, data[2], p0=[12000, 0.1, 1])
    print(params[2])

    plt.figure(figsize=(6, 4))
    # plt.scatter(x_data, y_data, label='Data')
    plot_x_start = 0
    plot_x_finish = 240
    full_x_values = range(plot_x_start, plot_x_finish)
    phase_angle = 0 if params[0] > 0 else math.pi
    plt.plot(full_x_values, sin_wave(full_x_values, params[0], params[1], phase_angle),label='Fitted function', color='#D3D3D3')
        

    # shifted_x_values = [(x + math.copysign((params[2] / params[1]), params[0])) for x in x_values]
    if params[0] > 0:
        shifted_x_values = [(x + (params[2] / params[1])) for x in x_values]
    else:
        shifted_x_values = [(x + (params[2] / params[1]) + 31) for x in x_values]

    for i in range(len(data)):
        plt.plot(shifted_x_values, data[i], label=labels[i])
 
    # Customize the plot
    print(os.path.basename(filename))
    plt.title(os.path.basename(filename))
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.xlim(plot_x_start, plot_x_finish)
    plt.ylim(-20000, 20000)
    # plt.legend()
    # print(arg, formatNumbers(THD_Values))
    # Save the plot to a file (e.g., in PNG format)
    # output_filename = str(int(math.copysign((params[2] / params[1]), params[0]))) + ' ' + os.path.splitext(arg)[0] + ".png"  # Change the filename and format as needed
    output_filename = os.path.splitext(filename)[0] + ".png"  # Change the filename and format as needed
    plt.savefig(output_filename, format="png")


def main():
    arg = sys.argv[1]
    # print(arg)
    data = jgrab.parse_file(arg)
    print(data)
    plot(data, arg)
    
    



if __name__ == "__main__":
    main()
