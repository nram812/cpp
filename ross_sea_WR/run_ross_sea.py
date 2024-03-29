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
from joblib import load
# output this as an xlsx
# climatology periods are all consistent and from 1981 to 2010
# ingest the twice daily data
from sklearn.decomposition import PCA

# Obtain the names of the synoptic types from the original paper

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

clim_period = tuple(np.array(config_RSWR["clim_period"]).astype('int'))  # climatological `normal`

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
                             parallel=True)
    dset = dset.load()
    dset = dset.reindex(time=sorted(dset.time.values))

clim = xr.open_dataset(f'./ross_sea_WR/metadata/params/climatology_'
                       f'{config_RSWR["var_name"]}_{config_RSWR["level"]}_1_2_harmonics.nc')
# loading the climatology
# adding exception when harmonics are not required
if config_RSWR["clim_harmonic"] == "True":
    data = clim[config_RSWR["var_name"]].data
    dset[f'{config_RSWR["var_name"]}_deseason'] = \
        dset[config_RSWR["var_name"]].groupby(dset.time.dt.dayofyear) \
        - clim[f"{config_RSWR['var_name']}_harmonics"]
else:
    data = clim[config_RSWR["var_name"]].data
    dset[f'{config_RSWR["var_name"]}_deseason'] = \
        dset[config_RSWR["var_name"]].groupby(dset.time.dt.dayofyear) \
        - clim[f"{config_RSWR['var_name']}"]


dset[f'{config_RSWR["var_name"]}_deseason_detrend'] =\
    detrend_dim(dset[f'{config_RSWR["var_name"]}_deseason'], 'time')
trend = (dset[f'{config_RSWR["var_name"]}_deseason'] -\
         dset[f'{config_RSWR["var_name"]}_deseason_detrend'])
ave = dset[f'{config_RSWR["var_name"]}_deseason'].mean('time')
std = dset[f'{config_RSWR["var_name"]}_deseason'].std('time')
ave_detrend = dset[f'{config_RSWR["var_name"]}_deseason_detrend'].mean('time')
std_detrend = dset[f'{config_RSWR["var_name"]}_deseason_detrend'].std('time')

dset[f'{config_RSWR["var_name"]}_deseason_std'] = (dset[f'{config_RSWR["var_name"]}_deseason'] - ave) / std
dset[f'{config_RSWR["var_name"]}_deseason_detrend_std'] = \
    (dset[f'{config_RSWR["var_name"]}_deseason_detrend'] - ave_detrend) / std_detrend
# changed the area weights on the scropt
area_weights = area_grid(dset['lat'], dset['lon'], return_dataarray=True)
dset['area_weights'] = area_weights
dset['area_weights'] = (dset['area_weights'] / dset['area_weights'].mean(['lat','lon']))

if config_RSWR["detrend"] == "True":

    if config_RSWR["standardize"] == "True":

        dset_to_eof = dset[f'{config_RSWR["var_name"]}_deseason_detrend_std'] * dset['area_weights']

    else:

        dset_to_eof = dset[f'{config_RSWR["var_name"]}_deseason_detrend'] * dset['area_weights']

else:

    if config_RSWR["standardize"] == "True":

        dset_to_eof = dset[f'{config_RSWR["var_name"]}_deseason_std'] * dset['area_weights']

    else:

        dset_to_eof = dset[f'{config_RSWR["var_name"]}_deseason'] * dset['area_weights']
# defining the land mask
lsmask = lsmask.sel(lon=slice(*config_RSWR["domain"][:2]), lat=slice(*config_RSWR["domain"][2:]))
mask = lsmask['land'].where(lsmask['land'] == 0)
mask = mask.where(np.isnan(mask), 1)
dset_to_eof_masked = dset_to_eof * mask
dset_to_eof_masked = dset_to_eof_masked.stack(z=('lat', 'lon'))
dset_to_eof_masked = dset_to_eof_masked.dropna(dim='z')
pca = load('./ross_sea_WR/metadata/models/pca.joblib')
eofs = pca.components_
pcs = pca.transform(dset_to_eof_masked.data)
evf = pca.explained_variance_ratio_

eofs_dset = {}
eofs_dset['z'] = (dset_to_eof_masked.z)
eofs_dset['EOF'] = (('EOF'), np.arange(eofs.shape[0]) + 1)
eofs_dset[f'{config_RSWR["var_name"]}'] = (('EOF', 'z'), eofs)
eofs_dset = xr.Dataset(eofs_dset)
eofs_dset = eofs_dset.unstack('z')

# computing the pcs
pcs_df = pd.DataFrame(pcs, index=dset_to_eof.time.to_index())
pcs_df.columns = [f"PC{i}" for i in np.arange(pcs.shape[1]) + 1]

k_means = load('./ross_sea_WR/metadata/models/kmeans.joblib')
predicted_labels = k_means.predict(pcs_df)
clusters = pd.DataFrame(data={'cluster': predicted_labels + 1},
                        index=pcs_df.index)
clusters.to_excel(r'./ross_sea_WR/data/ross_sea_WR_labels.xlsx')
