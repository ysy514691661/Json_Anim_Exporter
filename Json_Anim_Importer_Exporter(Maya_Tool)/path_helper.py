"""
A helper moduel to help script in maya script editor get relative path, 
please put it into the python script folder of maya,
ex.C:\Users\Administrator\Documents\maya\2018\scripts
"""

import os

def get_module_file_path():
    return(__file__)

def get_module_dir_path():
    return(os.path.dirname(__file__))

def get_module_file_name():
    return(os.path.basename(__file__))
