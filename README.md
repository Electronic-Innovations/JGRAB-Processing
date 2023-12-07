---
# jgrab_processing

Program for processing and graphing the data in JGRAB files.

## Setting up the environment

Once the project files have been cloned you can setup the python environment for running and modifying the program. This project needs Python version 3 and was developed with version 3.10.

To create a virtual environment run the following command from the project folder

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages

```bash
pip install -r requirements.txt
```

## Usage

To run the program from the command line. You can point it at a single file

```bash
python -m jgrab_processing -f ./tests/examples/example_data/FullJGRAB.txt
```

Or you can point it at an entire folder.

```bash
python -m jgrab_processing -f ./tests/examples/example_data
```

## Command line options
-f force, Without this switch the program will only process data files that haven't been processed before. If you give this switch then it will process all files.