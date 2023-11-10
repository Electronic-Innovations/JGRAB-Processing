import os
from jgrab_processing.jgrab import parse_string, parse_file

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