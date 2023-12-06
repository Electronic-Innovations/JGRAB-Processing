import os
import sys
import math

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

#import jgrab

from scipy import optimize


def rms(numbers: list[float]) -> float:
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


def formatNumbers(numbers: float) -> str:
    return ["{:.2f}".format(number) for number in numbers]


def sin_wave(x: list[float],
             amplitude: float,
             frequency: float,
             phase: float) -> list[float]:
    return amplitude * np.sin((2 * math.pi * frequency * x) + phase)


def THD_N(x_values: list[float],
          y_values: list[float],
          p0=[350.0, 50.0, 0.0]) -> float:
    """
    Fits a sin wave to the waveform of the provided data. This is the
    fundamental frequency of the provided data. Then it calculates the
    difference between the original data and the fundamental sin wave,
    this is the noise. The RMS of the noise is then divided by the RMS
    of the original and multiplied by 100, giving us the Total Harmonic
    Distortion plus Noise as a percentage.

    The calculation of the fundamental can be inaccurate. You probably
    want to provide a reasonable p0 array to get it started in the
    right ballpark

    p0 = [amplitude, frequency, phase shift]
    """
    params, params_covariance = optimize.curve_fit(sin_wave,
                                                   x_values,
                                                   y_values,
                                                   p0)
    fundamental = sin_wave(x_values, params[0], params[1], params[2])
    noise = y_values - fundamental
    return (rms(noise) / rms(fundamental) * 100)


def process_data(data: list[list[int]]) -> pl.dataframe:
    frame = pl.DataFrame(data)
    labels = ['Dc-V', 'Sph-Unscaled', 'RphV', 'Rphl-Unscaled', 'SphV']
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
    params, params_covariance = optimize.curve_fit(
                                    sin_wave,
                                    data.to_series(0),
                                    data.to_series(1),
                                    [350.0, 50.0, 0.0])
    return params


def plot(data: pl.dataframe,
         sin_wave_params_r: list[float],
         sin_wave_params_s: list[float],
         filename: str):
    fig, axs = plt.subplots(3, 1, figsize=(16, 10))
    plot_x_start = 0
    plot_x_finish = (127 * 0.02) / 64
    full_x_values = np.arange(plot_x_start, plot_x_finish, 0.0001)
    # phase_angle = 0 if sin_wave_params_r[0] > 0 else math.pi

    sin_wave_values_r = sin_wave(full_x_values,
                                 sin_wave_params_r[0],
                                 sin_wave_params_r[1],
                                 sin_wave_params_r[2])
    axs[0].plot(full_x_values,
                sin_wave_values_r,
                label='Fitted function',
                color='#D3D3D3')

    sin_wave_values_s = sin_wave(full_x_values,
                                 sin_wave_params_s[0],
                                 sin_wave_params_s[1],
                                 sin_wave_params_s[2])
    axs[0].plot(full_x_values,
                sin_wave_values_s,
                label='Fitted function s',
                color='#D3D3D3')

    axs[0].plot(data.to_series(5), data.to_series(2))
    r_THD = THD_N(data.to_series(5), data.to_series(2))

    axs[0].plot(data.to_series(5), data.to_series(4))
    s_THD = THD_N(data.to_series(5), data.to_series(4))

    # Customize the plot
    axs[0].set_title(os.path.basename(filename))
    axs[0].set_xlim(plot_x_start, plot_x_finish)
    axs[0].set_ylim(-400, 400)
    axs[0].set_ylabel("Voltage (VAC)")
    axs[0].annotate("R THD+N {:.1f}%".format(r_THD), xy=(0, 360))
    axs[0].annotate("S THD+N {:.1f}%".format(s_THD), xy=(0, 320))
    axs[0].grid(True, linewidth=0.2, alpha=0.4)

    axs[1].plot(data.to_series(5), data.to_series(3))
    axs[1].plot(data.to_series(5), data.to_series(1))
    axs[1].set_xlim(plot_x_start, plot_x_finish)
    axs[1].set_ylim(-85, 85)
    axs[1].set_ylabel("Current (A)")
    axs[1].grid(True, linewidth=0.2, alpha=0.4)

    axs[2].plot(data.to_series(5), data.to_series(0))
    axs[2].set_xlim(plot_x_start, plot_x_finish)
    axs[2].set_ylim(-10, 850)
    axs[2].set_ylabel("Voltage (VDC)")
    axs[2].set_xlabel("Time (sec)")
    axs[2].grid(True, linewidth=0.2, alpha=0.4)

    plt.tight_layout()
    # Change the filename and format as needed
    output_filename = os.path.splitext(filename)[0] + ".png"
    plt.savefig(output_filename, format="png")
    plt.close()


def main():
    arg = sys.argv[1]
    # data = jgrab.parse_file(arg)
    # plot(data, arg)


if __name__ == "__main__":
    main()
