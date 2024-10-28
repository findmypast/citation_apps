# basic common utilities file

def get_creds():
    # get creds from .txt & return as creds dict
    creds = {}
    with open("creds.txt") as f:
        for line in f:
            (key, val) = line.split()
            creds[key] = val
    return creds


def get_cdo_struct():
    cdo_struct = {}
    with open("cdo_structure.txt") as f:
        for line in f:
            (key, val) = line.split(':')
            cdo_struct[key] = val
    return cdo_struct
