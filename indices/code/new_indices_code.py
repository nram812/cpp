import warnings
import os, sys
import glob
import pathlib
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import requests
import matplotlib as mpl
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
import pandas as pd
from dask.diagnostics import ProgressBar
os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')

tahiti_coords = (-17.535000, -149.5695)
darwin_coords = (-12.43806, 130.84111)
# This code creates the indices of interest
warnings.simplefilter(action="ignore", category=FutureWarning)

# loading the raw historical data
complete_dset = xr.open_dataset(r"data/monthly_single_levels_era5_complete.nc", chunks={"time":10})
complete_dset['longitude'] = np.arange(0,180, 0.25).tolist() + np.arange(-180,0, 0.25).tolist()
complete_dset = complete_dset.reindex(longitude = np.arange(-180,180,0.25))

# Reindexing the data, this arises from an issue with a different coordinate system
# complete dset ends on 2021-04-1
load_downloaded_dset = xr.open_mfdataset(r"data/single-levels/*/*.nc", parallel = True)
resampled = load_downloaded_dset.resample(time = '1MS').mean()

# load daily dataset of trenberth


def subtract_clim(df, period = ["1981","2010"]):
    return df.groupby(df.time.dt.month).apply(lambda a: a- a.sel(time = slice(period[0], period[1])).mean("time"))


with ProgressBar():
    merged = xr.merge([resampled, complete_dset.interp_like(resampled.isel(time=0), method='nearest')])
    #merged = merged.chunk({"latitude": 10, "longitude": 10})
    merged = subtract_clim(merged)


def count_sst_nans(df):
    nans_in_last_time_step = np.isnan(df['sst'].isel(time =-1).values).sum()
    nans_in_first_time_step = np.isnan(df['sst'].isel(time =0).values).sum()
    if nans_in_last_time_step > nans_in_first_time_step:
        sys.exit(1)
        # exit the program as there too many nan values
    else:
        return True

def standardize(x):
    anoms = (x - x.sel(time =slice("1981","2010")).mean("time"))
    return anoms/anoms.std("time")
# if the data is okay
# here is a preliminary check

# computing the index0.
with ProgressBar():
    if count_sst_nans(merged):
        tahiti = standardize(merged['msl'].interp(latitude = tahiti_coords[0], longitude = tahiti_coords[1]))
        darwin = standardize(merged['msl'].interp(latitude = darwin_coords[0], longitude = darwin_coords[1]))
        msd = np.sqrt(np.nanmean((tahiti - darwin)**2))

        soi = (tahiti - darwin) / msd
        soi = soi.compute()#standardize(soi).compute()
with ProgressBar():
    z1 = merged['sst'].rolling(latitude = 8).apply(lambda a: np.nanmean(a)).rolling(longitude = 8).apply(lambda a: np.nanmean(a)).compute()
iod_data = merged['sst'].interp(latitude = sst_anoms.latitude.values,
                                longitude = sst_anoms.longitude.values,
                                method='linear')

z1 =aggregate_da(merged['sst'].isel(time =slice(0, None)).isel(latitude = slice(0,480),
                                                  longitude = slice(0,1440)), {'latitude': 4, 'longitude': 4})

iod_data = z1.interp(latitude = sst_anoms.latitude.values,
                                longitude = sst_anoms.longitude.values,
                                method='linear')
sst_anoms = xr.open_dataset(f'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/sst_anoms.nc')
fig,ax = plt.subplots(2)
z1.isel(time =-2).plot(ax =ax[0])
sst_anoms['sst'].isel(time =-1).plot(ax =ax[1])
fig.show()


import xarray as xr
from skimage.measure import block_reduce
def aggregate_da(da, agg_dims, suf='_agg'):
    input_core_dims = list(agg_dims)
    n_agg = len(input_core_dims)
    core_block_size = tuple([agg_dims[k] for k in input_core_dims])
    block_size = (da.ndim - n_agg)*(1,) + core_block_size
    output_core_dims = [dim + suf for dim in input_core_dims]
    output_sizes = {(dim + suf): da.shape[da.get_axis_num(dim)]//agg_dims[dim]
                    for dim in input_core_dims}
    output_dtypes = da.dtype
    da_out = xr.apply_ufunc(block_reduce, da, kwargs={'block_size': block_size},
                            input_core_dims=[input_core_dims],
                            output_core_dims=[output_core_dims],
                            output_sizes=output_sizes,
                            output_dtypes=[output_dtypes],
                            dask='parallelized')
    for dim in input_core_dims:
        new_coord = block_reduce(da[dim].data, (agg_dims[dim],), func=np.nanmean)
        da_out.coords[dim + suf] = (dim + suf, new_coord)
    return da_out
aggregate_da(da, {'lat': 2, 'lon': 2})

# darwin coordinates
soi_test = pd.read_excel(r"/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/data/niwa-soi-latest.xlsx",
                         index_col=0, parse_dates=True)
soi_test2 = soi.to_dataframe()

fig,ax = plt.subplots()
soi_test['SOI'].plot(ax = ax)
soi_test2['msl'].loc["2016":].plot(ax =ax)
fig.show()

fig, ax = plt.subplots(2)
nino34 = merged['sst'].sel(latitude = slice(5, -5),
                           longitude = slice(-170,-120)).mean(["latitude",
                                                               "longitude"]).compute()
merged['sst'].isel(time =-17).plot(ax = ax[0], vmin =-2, vmax =2, cmap='RdBu_r')
#resampled['msl'].isel(time =-1).plot(ax = ax[1])
fig.show()
fig, ax = plt.subplots()
nino34.rolling(time = 5).mean().isel(time = slice(-55,None)).plot(ax = ax)
fig.show()