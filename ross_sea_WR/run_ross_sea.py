### os
import os
import sys
from sklearn.cluster import KMeans
### datetimes
from datetime import datetime, timedelta
### scipy
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import cartopy.crs as ccrs
import dask
from dask.diagnostics import ProgressBar
from tqdm import tqdm
import json
from functools import partial
from matplotlib import pyplot as plt
import matplotlib
import seaborn as sns

### scikit-learn
from sklearn.decomposition import PCA

np.random.seed(42)
with open('./config.json', 'r') as f:
    config = json.load(f)
config_RSWR = config["Ross_Sea_WR"]
sys.path.append(f'{config["repository"]}')
from SPBI.src import *

sys.path.append(r'./lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *

varname = config_RSWR["var_name"]
level = config_RSWR["level"]
first_year = int(
    config_RSWR["first_year"])  # can select the first year for analysis here, leave to `None` for all period available
last_year = int(config_RSWR["last_year"])
domain = config_RSWR["domain"]  # domain is Southern Hemisphere
clim_period = tuple(np.array(config_RSWR["clim_period"]).astype('int'))  # climatological `normal`
lat_name = config_RSWR["lat_name"]  # should always be `lat`
lon_name = config_RSWR["lon_name"]  # should always be `lon`
add_cyclic = config_RSWR["add_cyclic"]  # whether we need to add a cyclic point
clim_harmonic = config_RSWR["clim_harmonic"]  # harmonic analysis on the time mean (day of year averages) or 'raw' data
standardize = config_RSWR["clim_harmonic"]
detrend = config_RSWR["detrend"]

lsmask = xr.open_dataset(r'./ross_sea_WR/land.nc', decode_times=False)
lsmask = lsmask.sortby('lat')
lsmask = lsmask.squeeze()
# Adding the custom import statements to the code
years, months, mFMT, yFMT = load_plotting_config__()
dpath = pathlib.Path(config['output_daily_ncep_directory'])
lfiles = sorted(list(dpath.glob("hgt.????.nc")))

# %%
with ProgressBar():
    dset = xr.open_mfdataset(lfiles,
                             preprocess=partial(preprocess,
                                                level=config_RSWR['level'],
                                                domain=config_RSWR['domain']),
                             parallel=True).load()
    dset = dset.reindex(time=sorted(dset.time.values))

if 'time_bnds' in dset.variables:
    dset = dset.drop('time_bnds')
if len(list(dset.data_vars)) >= 1:
    varid = list(dset.data_vars)[0]

dset = dset.sel(time=slice(str(first_year), str(last_year)))
clim = dset.sel(time=slice(str(clim_period[0]), str(clim_period[-1])))
clim = dset.groupby(dset.time.dt.dayofyear).mean('time')
with ProgressBar():
    clim.compute()
    clim.load()

if clim_harmonic == "True":
    data = clim[varid].data
    season = np.apply_along_axis(harmo, 0, data, **{'nbharm': 2})
    clim[f"{varid}_harmonics"] = (('dayofyear', lat_name, lon_name), season)
    dset[f'{varid}_deseason'] = dset[varid].groupby(dset.time.dt.dayofyear) - clim[f"{varid}_harmonics"]
    if clim_harmonic:
        data = clim[varid].data
        season = np.apply_along_axis(harmo, 0, data, **{'nbharm': 2})
        clim[f"{varid}_harmonics"] = (('dayofyear', lat_name, lon_name), season)
        dset[f'{varid}_deseason'] = dset[varid].groupby(dset.time.dt.dayofyear) - clim[f"{varid}_harmonics"]
# Modify SPBI aspects of the code

# compute the climatology, including the harmonics
clim = dset.sel(time=
                slice(*tuple(config_spbi['clim_period'])))
clim = clim.groupby(clim.time.dt.dayofyear).mean('time')

data = clim[config_spbi["var_name"]].data
season = np.apply_along_axis(harmo, 0, data, **{'nbharm': 2})
# climatology based on harmonics
clim[f"{config_RSWR['var_name']}_harmonics"] = (('dayofyear', config_RSWR['lat_name'], config_RSWR['lon_name']), season)
dset[f'{config_RSWR["var_name"]}_deseason'] = dset[config_RSWR["var_name"]].groupby(dset.time.dt.dayofyear) - clim[
    f"{config_RSWR['var_name']}_harmonics"]
clim.to_netcdf(
    f'./ross_sea_WR/metadata/params/climatology_{config_spbi["var_name"]}_{config_spbi["level"]}_1_2_harmonics.nc')
# anomalies are computed lreative to these harmonics


dset[f'{varid}_deseason_detrend'] = detrend_dim(dset[f'{varid}_deseason'], 'time')
trend = (dset[f'{varid}_deseason'] - dset[f'{varid}_deseason_detrend'])
ave = dset[f'{varid}_deseason'].mean('time')
std = dset[f'{varid}_deseason'].std('time')
ave_detrend = dset[f'{varid}_deseason_detrend'].mean('time')
std_detrend = dset[f'{varid}_deseason_detrend'].std('time')

dset[f'{varid}_deseason_std'] = (dset[f'{varid}_deseason'] - ave) / std
dset[f'{varid}_deseason_detrend_std'] = \
    (dset[f'{varid}_deseason_detrend'] - ave_detrend) / std_detrend

area_weights = area_grid(dset['lat'], dset['lon'], return_dataarray=True)
dset['area_weights'] = area_weights

if detrend == "True":

    if standardize == "True":

        dset_to_eof = dset[f'{varid}_deseason_detrend_std'] * dset['area_weights']

    else:

        dset_to_eof = dset[f'{varid}_deseason_detrend'] * dset['area_weights']

else:

    if standardize == "True":

        dset_to_eof = dset[f'{varid}_deseason_std'] * dset['area_weights']

    else:

        dset_to_eof = dset[f'{varid}_deseason'] * dset['area_weights']
# defining the land mask
lsmask = lsmask.sel(lon=slice(*domain[:2]), lat=slice(*domain[2:]))
mask = lsmask['land'].where(lsmask['land'] == 0)
mask = mask.where(np.isnan(mask), 1)
dset_to_eof_masked = dset_to_eof * mask
dset_to_eof_masked = dset_to_eof_masked.stack(z=('lat','lon'))
dset_to_eof_masked = dset_to_eof_masked.dropna(dim='z')

pca = PCA(n_components=0.90)
pca = pca.fit(dset_to_eof_masked.data)
eofs = pca.components_
pcs = pca.transform(dset_to_eof_masked.data)
evf = pca.explained_variance_ratio_

eofs_dset = {}
eofs_dset['z'] = (dset_to_eof_masked.z)
eofs_dset['EOF'] = (('EOF'), np.arange(eofs.shape[0]) + 1)
eofs_dset[varid] = (('EOF','z'), eofs)
eofs_dset = xr.Dataset(eofs_dset)
eofs_dset = eofs_dset.unstack('z')

# computing the pcs
pcs_df = pd.DataFrame(pcs, index=dset_to_eof.time.to_index())
pcs_df.columns = [f"PC{i}" for i in np.arange(pcs.shape[1]) + 1]



# fig, ax = plt.subplots()
# area_weights.plot(ax = ax)
# fig.show()
# Clipping the area weights as zero.
# Normalize the area the weights.
# Cosine of the angle
dset['area_weights'] = area_weights
dset['area_weights'] = (dset['area_weights'] / dset['area_weights'].mean(['lat', 'lon']))
dset_to_eof = dset[f'{config_spbi["var_name"]}_deseason_filtered_detrend'] * \
              dset['area_weights']
dset_to_eof = dset_to_eof.stack(z=('lat', 'lon')).sel(time=slice(*tuple(config_spbi['clim_period'])))

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

arr_deseason = dset[f'{config_spbi["var_name"]}_deseason'] * dset['area_weights']
arr_deseason = arr_deseason.stack(z=('lat', 'lon'))
eof1 = eofs_dset.sel(EOF=1)
eof2 = eofs_dset.sel(EOF=2)
eof1 = eof1.stack(z=('lat', 'lon'))[config_spbi["var_name"]]
eof2 = eof2.stack(z=('lat', 'lon'))[config_spbi["var_name"]]

pc1 = arr_deseason.dot(eof1)
pc2 = arr_deseason.dot(eof2)

# import seaborn as sns
# fig, ax = plt.subplots()
# sns.histplot(pc1.values, ax = ax)
# fig.show()
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
number_of_lagged_times_in_plot = 96
pc1_data = pc1std.to_dataframe(name="SPBI")
dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=pc1_data.iloc[-number_of_lagged_times_in_plot:],
                                                        col1='SPBI', col2='SPBI', weekly=None)

fig, ax, __, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                         soim, months,
                                                         output_path=f'./SPBI/figures',
                                                         cei=True, var_name=f'NIWA South Pacific Blocking Index (SBPI)',
                                                         var_2='', title=False, label_bool=None,
                                                         period1=1, period2=14, periodicity='D', ylim=(-3, 3),
                                                         figsize=(14, 10))
add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
              data_source="http://www.niwa.co.nz/CPPdata",
              ref="Ref: Limpasuvan, V., & Hartmann, D. L. (1999); DOI: 10.1029/1999GL010478")
ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
ax.grid(False)
fig.show()
fig.savefig(f'./SPBI/figures/SPBI_PC_index.png', dpi=300)
