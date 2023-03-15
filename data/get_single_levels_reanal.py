from __future__ import print_function
import cdsapi
import datetime as dt
from dask import delayed, compute
from dask.diagnostics import ProgressBar
import numpy as np
import os
import pandas as pd
import xarray as xr
import signal
import sys
import threading



try:
    import thread
except ImportError:
    import _thread as thread
from time import sleep
try:
    range, _print = xrange, print
    def print(*args, **kwargs):
        flush = kwargs.pop('flush', False)
        _print(*args, **kwargs)
        if flush:
            kwargs.get('file', sys.stdout).flush()
except NameError:
    pass
def quit_function(fn_name):
    # print to stderr, unbuffered in Python 2.
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush() # Python 3 stderr is likely buffered.
    thread.interrupt_main() # raises KeyboardInterrupt

def exit_after(s):
    '''
    use as decorator to exit process if
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer
# Defining the data of the output path
output_path = r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices'
# Definig the current dates
current_date = dt.datetime.utcnow().date()
output_log = f'{output_path}/data/logs/{current_date.strftime("%Y-%m-%d.log")}'
min_lagged_offset = 5
# Defining the regions and variables of interest
single_variables = ['mean_sea_level_pressure', 'sea_surface_temperature', 'surface_pressure']
times = [ '00:00']
lat_N, lon_e, lat_s, lon_w = 60, -180, -60, 180
region = [lat_N, lon_e, lat_s, lon_w]

# Load the client

@exit_after(600)
def download_data(
        year, month, output_fname, lat_N = lat_N, lon_e = lon_e, lat_s = lat_s, lon_w = lon_w,
                  variable_type ='reanalysis-era5-single-levels'):


    dict_inputs =     {
    'product_type': 'reanalysis',
    'variable': [
        'mean_sea_level_pressure', 'sea_surface_temperature', 'surface_pressure',
    ],
    'year': year,
    'month': month,
    'day': [
        '01', '02', '03',
        '04', '05', '06',
        '07', '08', '09',
        '10', '11', '12',
        '13', '14', '15',
        '16', '17', '18',
        '19', '20', '21',
        '22', '23', '24',
        '25', '26', '27',
        '28', '29', '30',
        '31',
    ],
    'time': [
        '00:00'
    ],
    'format': 'netcdf',
    'area': [
        lat_N, lon_e, lat_s,
        lon_w,
    ]
}

    return c.retrieve(variable_type, dict_inputs, output_fname)


def check_filenames(fnames, output_log):
    logger = []
    fnames = fnames[0]
    bool_file = True
    if not os.path.exists(fnames):
        logger.append(fnames)
        bool_file = True
    logs = pd.DataFrame(logger)
    logs.to_csv(output_log)
    return bool_file

def format_day(day):
    day = int(day)
    if day >=10:
        return str(day)
    else:
        return f"0{day}"
if __name__ == "__main__":
    # Defining the client
    c = cdsapi.Client()
    # Loop through the lagged times of interest
    filenames = []
    lists = []
    ref_time = current_date -dt.timedelta(days = int(min_lagged_offset))
    year = str(ref_time.year)
    month = format_day(ref_time.month)
    day = ref_time.day

    # Creating a string for the pressure level data
    ref_single = f'{output_path}/data/single-levels/{year}'
    if not os.path.exists(ref_single):
        os.makedirs(ref_single)
    # make a path if it doesnt exist
    output_single = f'{ref_single}/single_levels_{year}_{month}.nc'
    # Logging the files that have been downloaded
    filenames.append(output_single)
    # define a timeout time
    # set am alarm

    # If the data already exists we will not download the data

    if not os.path.exists(output_single):
        # Download the tasksyear, month, output_fname
        download_data(year, month, output_single,lat_N = lat_N, lon_e = lon_e, lat_s = lat_s, lon_w = lon_w,
                  variable_type ='reanalysis-era5-single-levels')
    else:
        df = xr.open_dataset(output_single)
        # loading the dataset incase it fails
        os.remove(output_single)
        download_data(year, month, output_single,lat_N = lat_N, lon_e = lon_e, lat_s = lat_s, lon_w = lon_w,
                  variable_type ='reanalysis-era5-single-levels')
        if not check_filenames(filenames, output_log):
            # save the original file if the file fails
            df.to_netcdf(output_single)

