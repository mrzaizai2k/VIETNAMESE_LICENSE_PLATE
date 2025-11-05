import sys
sys.path.append("")

from functools import wraps
import time
import os
import yaml
import numpy as np
import cv2

        
def convert_ms_to_hms(ms):
    seconds = ms / 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    seconds = round(seconds, 2)
    
    return f"{int(hours)}:{int(minutes):02d}:{seconds:05.2f}"


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        time_delta = convert_ms_to_hms(total_time*1000)

        print(f'{func.__name__.title()} Took {time_delta}')
        return result
    return timeit_wrapper

def is_file(path:str):
    return '.' in path

def check_path(path):
    # Extract the last element from the path
    last_element = os.path.basename(path)
    if is_file(last_element):
        # If it's a file, get the directory part of the path
        folder_path = os.path.dirname(path)

        # Check if the directory exists, create it if not
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Create new folder path: {folder_path}")
        return path
    else:
        # If it's not a file, it's a directory path
        # Check if the directory exists, create it if not
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Create new path: {path}")
        return path

def read_config(path = 'config/config.yaml'):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def load_knn_model(config):
    """Load KNN model for character recognition"""
    npaClassifications = np.loadtxt(config["model"]["classifications_path"], np.float32)
    npaFlattenedImages = np.loadtxt(config["model"]["flattened_images_path"], np.float32)
    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))  # reshape to 1D

    kNearest = cv2.ml.KNearest_create()
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    return kNearest