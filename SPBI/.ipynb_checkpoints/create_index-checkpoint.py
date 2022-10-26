
import os
import sys
import shutil
from datetime import datetime, timedelta
import numpy as np
from scipy import signal
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import dask
from dask.diagnostics import ProgressBar
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt
import matplotlib
import requests
import urllib.request
import io
import pathlib
HOME = pathlib.Path.home()
CWD = pathlib.Path.cwd()
import matplotlib.path as mpath
np.random.seed(42)
import os
import wget
import datetime
import json
from functools import partial
with open('./config.json', 'r') as f:
    config = json.load(f)
config_spbi = config["SPBI_metadata"]
sys.path.append(f'{config["repository"]}')
from SPBI.src import *
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *
# Adding the custom import statements to the code
years, months, mFMT, yFMT = load_plotting_config__()

dpath = pathlib.Path(config['output_daily_ncep_directory'])
lfiles = sorted(list(dpath.glob("hgt.????.nc")))

# %%
with ProgressBar():
    dset = xr.open_mfdataset(lfiles,
                             preprocess=partial(preprocess,
                                                level = config_spbi['level'],
                                                domain = config_spbi['domain']),
                             parallel=True).load()
    dset = dset.reindex(time=sorted(dset.time.values))

# compute the climatology, including the harmonics
clim = dset.sel(time=
                slice(*tuple(config_spbi['clim_period'])))
clim = clim.groupby(clim.time.dt.dayofyear).mean('time')
# climatological average
data = clim[config_spbi["var_name"]].data
season = np.apply_along_axis(harmo, 0, data, **{'nbharm': 2})
# climatology based on harmonics
clim[f"{config_spbi['var_name']}_harmonics"] = (('dayofyear', config_spbi['lat_name'], config_spbi['lon_name']), season)
dset[f'{config_spbi["var_name"]}_deseason'] = dset[config_spbi["var_name"]].groupby(dset.time.dt.dayofyear) - clim[f"{config_spbi['var_name']}_harmonics"]
clim.to_netcdf(f'./SPBI/params/climatology_{varname}_{level}_1_2_harmonics.nc')
# anomalies are computed lreative to these harmonics

dset[f'{config_spbi["var_name"]}_deseason_filtered'] =\
    (('time', 'lat', 'lon'),
     np.apply_along_axis(low_pass_filter,
                         0,
                         dset[f'{config_spbi["var_name"]}_deseason'].data))
dset[f'{config_spbi["var_name"]}_deseason_filtered_detrend'] = \
    detrend_dim(dset[f'{config_spbi["var_name"]}_deseason_filtered'], 'time')

trend = (dset[f'{config_spbi["var_name"]}_deseason_filtered'] - dset[f'{config_spbi["var_name"]}_deseason_filtered_detrend'])


area_weights = area_grid(dset['lat'], dset['lon'], return_dataarray=True)
dset['area_weights'] = area_weights
dset_to_eof = dset[f'{config_spbi["var_name"]}_deseason_filtered_detrend'] *\
              dset['area_weights']
dset_to_eof = dset_to_eof.stack(z=('lat', 'lon')).sel(time = slice(*tuple(config_spbi['clim_period'])))

# PCA components
pca = PCA(n_components=3)
pca = pca.fit(dset_to_eof.data)
eofs = pca.components_
pcs = pca.transform(dset_to_eof.data)
evf = pca.explained_variance_ratio_
# Is the normalization stragey working?
eofs_dset = {}
eofs_dset['z'] = (dset_to_eof.z)
eofs_dset['EOF'] = (('EOF'), np.arange(config_spbi["neofs"]) + 1)
eofs_dset[config_spbi["var_name"]] = (('EOF', 'z'), eofs)
eofs_dset = xr.Dataset(eofs_dset)
eofs_dset = eofs_dset.unstack('z')
cbar_kwargs = {'aspect': 20, 'shrink': 0.7}

eofs_dset.to_netcdf(
    f"./SPBI/params/EOF_1_{config_spbi['neofs']}_{config_spbi['first_year']}_{config_spbi['last_year']}.nc")
try:
    shutil.rmtree('./SPBI/outputs/dset_Z500_SP_Blocking.zarr/')
except FileNotFoundError:
    pass
dset.to_zarr('./SPBI/outputs/dset_Z500_SP_Blocking.zarr')

# there appears to be some issues here
# (e.g. the multiplication by area weights)
# differences in the time periods also
f
arr_deseason = dset[f'{config_spbi["var_name"]}_deseason'] * dset['area_weights']
arr_deseason = arr_deseason.stack(z=('lat', 'lon'))
eof1 = eofs_dset.sel(EOF=1)
eof2 = eofs_dset.sel(EOF=2)
eof1 = eof1.stack(z=('lat', 'lon'))[config_spbi["var_name"]]
eof2 = eof2.stack(z=('lat', 'lon'))[config_spbi["var_name"]]
pc1 = arr_deseason.dot(eof1)
pc2 = arr_deseason.dot(eof2)

projected_EOF1_ave = pc1.sel(time=slice(*list(map(str, config_spbi["clim_period"])))).mean()
projected_EOF2_ave = pc2.sel(time=slice(*list(map(str, config_spbi["clim_period"])))).mean()
projected_EOF1_std = pc1.sel(time=slice(*list(map(str, config_spbi["clim_period"])))).std()
projected_EOF2_std = pc2.sel(time=slice(*list(map(str, config_spbi["clim_period"])))).std()

projected_EOFs_ave = xr.concat([projected_EOF1_ave, projected_EOF2_ave], dim='EOF')
projected_EOFs_std = xr.concat([projected_EOF1_std, projected_EOF2_std], dim='EOF')
projected_EOFs_ave = projected_EOFs_ave.to_dataset(name=config_spbi['var_name'])
projected_EOFs_std = projected_EOFs_std.to_dataset(name=config_spbi['var_name'])

projected_EOFs_ave.to_netcdf('./SPBI/params/projected_EOFs_ave.nc')
projected_EOFs_std.to_netcdf('./SPBI/params/projected_EOFs_std.nc')

pc1std = (pc1 - projected_EOF1_ave) / projected_EOF1_std
pc2std = (pc2 - projected_EOF2_ave) / projected_EOF2_std


sequences_pc1_df = extract_sequences(pc1std)
sequences_pc2_df = extract_sequences(pc2std)

for i, row in sequences_pc1_df.iterrows():
    dstart = row.event_start
    dend = row.event_end
    duration = row.event_duration
    pe = pc1std.sel(time=slice(dstart - timedelta(days=1), dend + timedelta(days=1)))
    if len(pe.where(pe >= 1).dropna(dim='time')) != duration:
        print(f"issue at date starting {dstart:%Y-%m-%d}")

# %%

for i, row in sequences_pc2_df.iterrows():
    dstart = row.event_start
    dend = row.event_end
    duration = row.event_duration
    pe = pc2std.sel(time=slice(dstart - timedelta(days=1), dend + timedelta(days=1)))
    if len(pe.where(pe >= 1).dropna(dim='time')) != duration:
        print(f"issue at date starting {dstart:%Y-%m-%d}")


sequences_pc1_df.to_csv('./SPBI/params/sequences_PC1_SE_Blocking.csv')
sequences_pc2_df.to_csv('./SPBI/params/sequences_PC2_SW_Blocking.csv')
number_of_lagged_times_in_plot =96
pc1_data = pc1std.to_dataframe(name = "SPBI")
dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=pc1_data.iloc[-number_of_lagged_times_in_plot:],
                                                        col1='SPBI', col2='SPBI', weekly = None)

fig, ax, __, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                         soim, months,
                                                         output_path=f'./SPBI/figures',
                                                         cei=True, var_name=f'NIWA South Pacific Blocking Index (SAM)',
                                                         var_2='', title=False, label_bool=None,
                                                         period1=1, period2=14, periodicity='D', ylim=(-3,3),
                                                         figsize=(14, 10))
add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
              data_source="http://www.niwa.co.nz/CPPdata",
              ref="Ref: Limpasuvan, V., & Hartmann, D. L. (1999); DOI: 10.1029/1999GL010478")
ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
ax.grid(False)
fig.show()
fig.savefig(f'./SPBI/figures/SPBI_PC_index.png',dpi=300)