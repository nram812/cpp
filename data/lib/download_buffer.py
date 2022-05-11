from __future__ import print_function
import sys
import threading
import cdsapi
import numpy as np
import os
# Function for donwloading data


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


@exit_after(600)
def download_data(
        year, month, output_fname, config,
                  variable_type ='reanalysis-era5-single-levels'):


    dict_inputs =     {
    'product_type': 'reanalysis',
    'variable': config["single_level_reanalysis"]["variables"],
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
    'time': config["single_level_reanalysis"]["times"],
    'format': 'netcdf',
    'area': [
        config["single_level_reanalysis"]["domain"]["lat_n"],
        config["single_level_reanalysis"]["domain"]["lon_e"],
        config["single_level_reanalysis"]["domain"]["lat_s"],
        config["single_level_reanalysis"]["domain"]["lon_w"],
    ]
}
    c = cdsapi.Client()

    return c.retrieve(variable_type, dict_inputs, output_fname)

def create_output_dirs(current_date):
    
    ref_time = current_date -dt.timedelta(days = np.int(min_lagged_offset))
    year = str(ref_time.year)
    month = str(ref_time.month).zfill(2)
    # check paths exst
    parent_dirs= f'{output_path}/data/era5-single-levels/{year}'
    output_fname = f'{parent_dirs}/single_levels_{year}_{month}.nc'
    if not os.path.exists(parent_dirs):
        os.makedirs(parent_dirs)
    # make a path if it doesnt exist
    return parent_dirs, output_fname, year, month
