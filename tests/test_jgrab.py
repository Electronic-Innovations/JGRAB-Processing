import os
import math
import polars as pl
import numpy as np
from jgrab_processing.jgrab import parse_string, parse_file
from jgrab_processing.base import fit_sin_wave, process_data, sin_wave, rms, THD_N

def test_jgrab_parse():
    input = """
 .. 
 <sp ok
JGRAB 
 -00028	% 2023-10-27   07:47:50
 -00036
 -00108
  00012
  00060
%% 0  -19993
 -00017
 -00009
  00095
  00039
  00039
%% 1  -19993
  00883
 -00339
 -00749
 -02035
 -03507
%% 2  -19993
 -00001
  00055
  00143
  00111
  00191
%% 3  -19993
  12256
  13120
  13408
  13280
  13536
%% 4  -19993 ok
    """
    output = parse_string(input, 10)
    assert output == [[-28,-36,-108,12,60],
                        [-17,-9,95,39,39],
                        [883,-339,-749,-2035,-3507],
                        [-1,55,143,111,191],
                        [12256,13120,13408,13280,13536]]

def test_jgrab_parse_file():
    filename = os.path.join(os.path.dirname(__file__), 'examples/FullJGRAB.txt')
    output = parse_file(filename, base = 10)
    assert len(output) == 5
    assert len(output[0]) == 128
    assert len(output[1]) == 128
    assert len(output[2]) == 128
    assert len(output[3]) == 128
    assert len(output[4]) == 128

def test_sin_wave():
    filename = os.path.join(os.path.dirname(__file__), 'examples/FullJGRAB.txt')
    data = parse_file(filename, base = 10)
    data_frame = process_data(data)
    b = data_frame.select(pl.col("time","RphV"))
    output = fit_sin_wave(b)
    answer = [-1.38577280e+04, 5.00424636e+01, -6.97262811e-02]
    result = np.allclose(output, answer, rtol=1e-05, atol=1e-08)
    print(output)
    #result = np.testing.assert_array_almost_equal_nulp(output, [-9.35116387e+05, 3.48670922e-04, 3.13470606e+00])
    #print(result)
    assert result
    
def test_generate_sin_wave():
    x_values = np.arange(0, 0.02, 0.005)
    y_values = sin_wave(x_values, 335.0, 50.0, 0.0)
    print(y_values)
    answer = [0.0, 335.0, 0.0, -335.0]
    assert np.allclose(y_values, answer, rtol=1e-05, atol=1e-08)
    
def test_rms():
    """
    Calculate the RMS value of a sin wave with a Vpeak of 335V and confirming that 
    it is about 240Vrms
    """
    x_values = np.arange(0, 1.0, 0.0001)
    y_values = sin_wave(x_values, 335.0, 50.0, 0.0)
    assert math.isclose(rms(y_values), 240, rel_tol=0.05)
    
def test_THD_N():
    """
    Calculating the THD of a signale that should only contain the fundamental
    and confirming that the result is close to 0.
    """
    x_values = np.arange(0, 1.0, 0.0001)
    y_values = sin_wave(x_values, 335.0, 50.0, 0.0)
    thd = THD_N(x_values, y_values)
    assert math.isclose(thd, 0, abs_tol=0.01)
    
def test_THD_N_2():
    """
    Adding a second sin wave to a fundamental and confirming that the THD
    calculation is about right.
    """
    x_values = np.arange(0, 1.0, 0.0001)
    fundamental = sin_wave(x_values, 335.0, 50.0, 0.0)
    harmonic = sin_wave(x_values, 20, 150, math.pi)
    y_values = [f + h for (f, h) in zip(fundamental, harmonic)]
    thd = THD_N(x_values, y_values)
    assert math.isclose(thd, 6, rel_tol=0.01)