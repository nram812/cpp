import sys
from matplotlib import pyplot as plt
import sys
import pathlib
import numpy as np
import pandas as pd
from cartopy import crs as ccrs
from pandas.plotting import register_matplotlib_converters
from scipy.stats import zscore
import xarray as xr
import glob


def demean(x):
    return x - x.sel(time=slice('1981', '2010')).mean('time')


def create_ersst_nc(lfiles_ersst, times, output_dirs ='./IOD/data'):
    d = []
    for i,fname in enumerate(lfiles_ersst):
        dset = xr.open_dataset(fname, decode_times=False)
        dset = dset.squeeze()
        dset.expand_dims("time")
        dset['time'] = (('time'), [times[i]])
        if 'lev' in dset.coords:
            dset = dset.drop('lev')
        #
        d.append(dset)

    dset = xr.concat(d, dim='time')
    try:
        dset.to_netcdf(f'{output_dirs}/sst_dset.nc')
    except:
        os.remove(f'{output_dirs}/sst_dset.nc')
        dset.to_netcdf(f'{output_dirs}/sst_dset.nc')
    dset = dset.sel(lat=slice(-20, 20), lon=slice(40, 120))
    dset = dset.sortby(dset.time)

    sst_anoms = dset['sst'].groupby('time.month').apply(demean)
    return dset, sst_anoms


def create_iod_series(sst_anoms):
    EAST = sst_anoms.sel(lon=slice(90, 110), lat=slice(-10,0)).mean('lat').mean('lon')
    WEST = sst_anoms.sel(lon=slice(50, 70), lat=slice(-10,10)).mean('lat').mean('lon')
    EAST = EAST.to_dataframe(name='EAST')
    WEST = WEST.to_dataframe(name='WEST')
    IOD = pd.concat([WEST, EAST], axis=1)
    IOD = IOD.apply(zscore)
    IOD = IOD.assign(IOD=IOD.WEST - IOD.EAST)
    return IOD
