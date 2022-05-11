from __future__ import print_function
import cdsapi
import datetime as dt
import numpy as np
import os
import pandas as pd
import xarray as xr
import sys
import json
sys.path.append('./lib')
from download_buffer import *
# load json file with config
with open('data_config.json', 'r') as f:
    config = json.load(f)
# Defining the data of the output path
output_path = config["single_level_reanalysis"]["output_path"]
current_date = dt.datetime.utcnow().date()
output_log = f'{output_path}/data/logs/{current_date.strftime("%Y-%m-%d.log")}'
min_lagged_offset = config["single_level_reanalysis"]["lagged_days"],


if __name__ == "__main__":
    # Defining the client
    parent_dirs, output_fname, year, month = create_output_dirs(current_date)
    try:
        os.remove(output_fname)
        download_data(year, month, output_fname, config
                  variable_type ='reanalysis-era5-single-levels')
    except FileNotFoundError:
            download_data(year, month, output_fname,config,
                variable_type ='reanalysis-era5-single-levels')

