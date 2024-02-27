import os
import sys

### datetimes
from datetime import datetime, timedelta

### scipy
import numpy as np
import pandas as pd
import xarray as xr
import dask
from dask.diagnostics import ProgressBar
from tqdm import tqdm

### plotting
from matplotlib import pyplot as plt
import matplotlib

### cartopy
from cartopy import crs as ccrs
from cartopy.util import add_cyclic_point

# %%

from eofs.xarray import Eof

# %%

import requests
import urllib.request
import io
os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
# defining the output data path
path = r"/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/"

# removed stanley as a coordinate
# original data doesn't span that time peridd - will redownload reanlaysis
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *
# Adding the custom import statements to the code
years, months, mFMT, yFMT = load_plotting_config__()

import pandas as pd
# %% md

### config

# %%

config = {}

config['NCEP1'] = {}
config['NCEP1']['MSLP'] = "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/surface/slp.mon.mean.nc"
config['NCEP1']['Z'] = "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/pressure/hgt.mon.mean.nc"
config['NCEP1']['start_year'] = 1948

config['NCEP2'] = {}
config['NCEP2']['MSLP'] = "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis2.derived/surface/mslp.mon.mean.nc"
config['NCEP2']['Z'] = "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis2.derived/pressure/hgt.mon.mean.nc"
config['NCEP2']['start_year'] = 1979

# %% md

### parameters

# %%

reanalysis = "NCEP1"
varname = "Z"
level = 850  # if not set, and 'Z' is selected instead of 'MSLP', it will default to 1000 hPa
first_year = None  # can select the first year for analysis here, leave to `None` for all period available
domain = [0, 360, -90, -20]  # domain is Southern Hemisphere
clim_period = [1991, 2020]  # climatological `normal`
lat_name = 'lat'  # should always be `lat`
lon_name = 'lon'  # should always be `lon`
std_per_month = True  # whether the std is subtracted to each month individually

# %% md

### get the URL

# %%

url = config[reanalysis][varname]

# %%

url

# %% md

### reads straight from the FTP / HTTPS URL

# %%

req = urllib.request.Request(url)

# %%

with urllib.request.urlopen(req) as resp:
    dset = xr.open_dataset(io.BytesIO(resp.read()))

# %%

dset

# %%

dset = dset.sortby('lat')

# %%

if 'time_bnds' in dset.variables:
    dset = dset.drop('time_bnds')

# %% md

### selections

# %%

if first_year is not None:
    if first_year >= config[reanalysis]['start_year']:
        dset = dset.sel(time=slice(str(first_year), None))
    else:
        print(
            f"The first year ({first_year}) needs to be >= to the start year in the {reanalysis} dataset: {config[reanalysis]['start_year']}")

if varname == 'Z':
    if level is not None:
        dset = dset.sel(level=level)
    else:
        dset = dset.sel(level=1000.)

# %% md

### selects the domain

# %%

dset = dset.sel(lon=slice(*domain[:2]), lat=slice(*domain[2:]))

# %%

dset

# %%

if len(list(dset.data_vars)) >= 1:
    varid = list(dset.data_vars)[0]

# %%

varid

# %% md

### adds a cyclic point

# %%

data = dset[varid]

# %%

lon = dset.coords[lon_name]
lon_idx = data.dims.index('lon')

# %%

wrap_data, wrap_lon = add_cyclic_point(data.values, coord=lon, axis=lon_idx)

# %%

dset_wrap = {}
dset_wrap['time'] = dset['time']
dset_wrap[lon_name] = ((lon_name), wrap_lon)
dset_wrap[lat_name] = dset[lat_name]
dset_wrap[varid] = (('time', lat_name, lon_name), wrap_data)

# %%

dset_wrap = xr.Dataset(dset_wrap)

# %%

dset = dset_wrap

# %%

dset_wrap.close()

# %%

del (dset_wrap)

# %% md

### calculates the climatology

# %%

climo = dset.sel(time=slice(*list(map(str, clim_period))))

# %%

climo = climo.groupby(climo.time.dt.month).mean('time')

# %% md

### quick plot of the climatology

# %%

for varid in climo.data_vars:
    climo[varid].plot(col='month', col_wrap=3)

# %% md

### calculates the anomalies

# %%

dset_anoms = dset.groupby(dset.time.dt.month) - climo

# %% md

### standardize per month ?

# %%

if std_per_month:
    print("\nwe standardize per month\n")


    def standardize(x):
        z = (x - x.sel(time=slice(f'{str(clim_period[0])}-01-01', f'{str(clim_period[-1])}-12-01')).mean(
            'time')) / x.std('time')
        return z


    dset_anoms = dset.groupby(dset_anoms.time.dt.month).apply(standardize)

# %% md

### then standardize (mean 0, std 1)

# %%

dset_anoms = (dset_anoms - dset_anoms.mean('time')) / dset_anoms.std('time')

# %%

f, ax = plt.subplots(ncols=2, figsize=(10, 5))
dset_anoms.mean('time')[varid].plot(ax=ax[0])
dset_anoms.std('time')[varid].plot(ax=ax[1])

# %% md

### weights by the square root of the cosine of the latitude

# %%

coslat = np.cos(np.deg2rad(dset_anoms.lat.data))

wgts = np.sqrt(coslat)[..., np.newaxis]

# %%

wgts[-1] = np.array([1e-9])

# %% md

### solve the EOF

# %%

solver = Eof(dset_anoms[varid], weights=wgts)

# %%

variance_fractions = solver.varianceFraction()

# %%

# variance_fractions[0]

# %%

eof1 = solver.eofsAsCorrelation(neofs=1)

# %%

# f, ax = plt.subplots(subplot_kw=dict(projection=ccrs.SouthPolarStereo(central_longitude=180)))
# eof1.squeeze().plot.contourf(ax=ax, levels=20, transform=ccrs.PlateCarree())
# ax.coastlines()

# %%

pc1 = solver.pcs(npcs=1, pcscaling=1)

# %%

pc1 = pd.DataFrame(pc1.data, index=dset_anoms.time, columns=[f'Monthly SAM index from {reanalysis} {varname}'])

# %%

#pc1.head()

# %%

#pc1.plot()

# %%


# %%
number_of_lagged_times_in_plot =48
dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=pc1.iloc[-number_of_lagged_times_in_plot:],
                                                        col1='Monthly SAM index from NCEP1 Z', col2='Monthly SAM index from NCEP1 Z')

fig, ax, __, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                         soim, months,
                                                         output_path=f'./SAM/figures',
                                                         cei=True, var_name=f'NIWA Southern Annular Mode (SAM)',
                                                         var_2='', title=False, label_bool=None,
                                                         period1=1, period2=3, periodicity='M', ylim=(-3,3),
                                                         figsize=(14, 10))
add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
              data_source="http://www.niwa.co.nz/CPPdata",
              ref="Ref: Limpasuvan, V., & Hartmann, D. L. (1999); DOI: 10.1029/1999GL010478")
ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
ax.grid(False)
    #fig.show()
fig.savefig(f'./SAM/figures/SAM_PC_index.png',dpi=300)
pc1.to_csv(f'./SAM/data_ncep/SAM_pc.csv')
pc1.to_excel(f'./SAM/data_ncep/SAM_pc.xlsx')


