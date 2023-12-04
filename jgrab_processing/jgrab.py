# https://www.vipinajayakumar.com/parsing-text-with-python/

def parse_string(jgrab: str, base: int = 10) -> list[list[int]]:
    """
    Parse a string that is in JGRAB format
    
    Parameters
    ----------
    jgrab : str
        String containing data in JGRAB format
    
    Returns
    -------
    array: list[list[int]]
        Parsed data in list of lists
    """
    
    # This function should fail
    
    start_reading_data = False
    data = [[],[],[],[],[]]
    timestamp = None
    col_index = 0
    
    for line in jgrab.splitlines():
        if line.startswith("JGRAB"):
            start_reading_data = True
        if start_reading_data:
            if line.startswith("%%"):
                col_index = col_index + 1
        
        parts = line.split()
        if len(parts) > 0: 
            try:
                value = int(line.split()[0], base = base)
                data[col_index].append(value)
            except ValueError:
                pass
    return data
    
def parse_file(path: str, base: int = 10) -> list[list[int]]:
    """
    Parse a text file containing JGRAB formatted data
    
    Parameters
    ----------
    path: str
        path to the file containing the data
    
    Returns
    -------
    array: list[list[int]]
        Parsed data in list of lists
    """
    with open(path) as file:
        return parse_string(file.read(), base = base)