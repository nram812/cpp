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
import cartopy.crs as ccrs

os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
warnings.simplefilter(action="ignore", category=FutureWarning)
# here the nino regions
# defining the regions for which we want to produce indicies for

regions = {'Nino 1+2': ((-10, 0), (-90, -80)),
           'Nino 2': ((-5, 5), (-150, -90)),
           'Nino 3.4': ((-5, 5), (-170, -120)),
           'Nino 4a': ((-5, 5), (160, 180)),
           'Nino 4b': ((-5, 5), (-180, -150)),
           'New Zealand': ((-55, -25), (160, 180))}
# Nino 4 region comprises of two subregions

tahiti_coords = (-17.535000, -149.5695)
darwin_coords = (-12.43806, 130.84111)
# This code creates the indices of interest


# loading the raw historical data
complete_dset = xr.open_dataset(r"data/monthly_single_levels_era5_complete.nc", chunks={"time": 50})

# Reindexing the data appropriately
complete_dset['longitude'] = np.arange(0, 180, 0.25).tolist() + np.arange(-180, 0, 0.25).tolist()
complete_dset = complete_dset.reindex(longitude=np.arange(-180, 180, 0.25))
complete_dset = complete_dset.reindex(latitude=sorted(complete_dset.latitude.values))

# Reindexing the data, this arises from an issue with a different coordinate system
# complete dset ends on 2021-04-1
load_downloaded_dset = xr.open_mfdataset(r"data/single-levels/*/*.nc", parallel=True)
resampled = load_downloaded_dset.resample(time='1MS').mean()
# reindexing the output in the same exact way
resampled = resampled.reindex(latitude=sorted(resampled.latitude.values))


# load daily dataset of trenberth
# functions to compute the sst


def count_sst_nans(df):
    nans_in_last_time_step = np.isnan(df['sst'].isel(time=-1).values).sum()
    nans_in_first_time_step = np.isnan(df['sst'].isel(time=0).values).sum()
    if nans_in_last_time_step > nans_in_first_time_step:
        sys.exit(1)
        # exit the program as there too many nan values
    else:
        return True


def standardize(x):
    """

    :param x: an xarray dataset with time as a key dimension
    :return: the zscore or normalized outputs
    """
    anomalies = (x - x.sel(time=slice("1981", "2010")).mean("time"))
    return anomalies / anomalies.std("time")


def subtract_clim(df, period=None):
    if period is None:
        period = ["1981", "2010"]
    return df.groupby(df.time.dt.month).apply(lambda a: a - a.sel(time=slice(period[0], period[1])).mean("time"))


# Merging the datasets


def extract_nino_regions(df, coords_list):
    """

    :param coords_list: A list of coordinates, see example
    :param df: a dataframe
    where nino1 = ((latmin, latmax), (lonmin, lonmax))

    :return:
    """
    d = {}
    for key, coords in coords_list.items():
        d[key] = df['sst'].sel(latitude=slice(*coords[0]),
                               longitude=slice(*coords[1]))
    return d


def plot_region(df_region, frequency='W',
                n_periods=3, subplot_kw={}, figsize=None):
    """
    plotting the spatial data
    :param figsize: size of figure
    :param subplot_kw: arguments for matplotlib subplots
    :param n_periods: the number of previous months you'd like to plot
    :param frequency: monthly or weekly ('M', or 'W')
    :param df_region: an xarray object
    :return:
    """
    if figsize is None:
        figsize = (8,8)

    lats, lons = np.meshgrid(df_region.latitude, df_region.longitude)
    lats = lats.T
    lons = lons.T
    # create plots for the last 3 weeks
    fig, ax = plt.subplots(nrows=1, ncols=n_periods, subplot_kw=subplot_kw, figsize=figsize)
    ax4 = fig.add_axes([0.05, 0.1, 0.9, 0.02])
    if n_periods == 1:
        ax = [ax]
    if frequency == 'W':
        for i in range(n_periods):
            times = df_region.time.to_index()[-22:]
            time_init = times[i * 7].strftime("%Y-%m-%d")
            times_end = times[i * 7 + 7].strftime("%Y-%m-%d")
            ax[i].set_title(f'{time_init} to {times_end}')
            plot_data = df_region.sel(time=slice(time_init, times_end)).mean("time")
            cs = ax[i].contourf(lons, lats, plot_data.values,
                                transform=ccrs.PlateCarree(),
                                cmap='RdBu_r', levels=np.arange(-1.5, 1.6, 0.1),
                                alpha=1, extend='both')
            ax[i].coastlines('50m', zorder=15)
    if frequency == 'M':
        for i in range(n_periods):
            times = df_region.time.to_index()[-n_periods:]
            time_init = times[-3:].strftime("%Y-%B")[i]
            # times_end = times[-n_periods +1].strftime("%Y-%m-%d")
            ax[i].set_title(f'{time_init}')
            plot_data = df_region.sel(time=time_init).mean("time")
            cs = ax[i].contourf(lons, lats, plot_data.values,
                                transform=ccrs.PlateCarree(),
                                cmap='RdBu_r', levels=np.arange(-1.5, 1.6, 0.1),
                                alpha=1, extend='both')
            ax[i].coastlines('50m', zorder=15)
    cbar = fig.colorbar(cs, orientation='horizontal', cax=ax4, pad=0.2)
    cbar.set_label('SST Anomaly (K)')
    return fig, ax


with ProgressBar():
    # select the common region,
    merged = xr.merge([resampled, complete_dset.interp_like(resampled.isel(time=0), method='nearest')])
    daily_merged = xr.merge([load_downloaded_dset, complete_dset.interp_like(resampled.isel(time=0), method='nearest')])
    merged = subtract_clim(merged)
    daily_anoms = subtract_clim(daily_merged).sel(time=load_downloaded_dset.time.to_index())
    # compute daily anomalies in real time
    if count_sst_nans(merged):
        tahiti = standardize(merged['msl'].interp(latitude=tahiti_coords[0], longitude=tahiti_coords[1]))
        darwin = standardize(merged['msl'].interp(latitude=darwin_coords[0], longitude=darwin_coords[1]))
        msd = np.sqrt(np.nanmean((tahiti - darwin) ** 2))
        soi = (tahiti - darwin) / msd
        soi = soi.compute().to_dataset().rename({"msl":'SOI'})
        soi.to.dataframe().to_csv(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/data/soi.csv')
        # saving the monthly southern oscillation index
        # compute the nino regions
        monthly_regions = extract_nino_regions(merged, regions)
        monthly_index_list = []
        for name, region in monthly_regions.items():
            monthly_index_list.append(region.mean(["latitude",
                                  "longitude"]).to_dataset().rename({"sst": name}).to_dataframe())
        monthly_index_list = pd.concat(monthly_index_list, axis=1)
        monthly_index_list.to_csv('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/data/monthly_index.csv')
        # daily index list
        daily_regions = extract_nino_regions(daily_anoms, regions)
        daily_index_list = []
        for name, region in daily_regions.items():
            daily_index_list.append(region.mean(["latitude",
                                  "longitude"]).to_dataset().rename({"sst": name}).to_dataframe())
        daily_index_list = pd.concat(daily_index_list, axis=1)
        daily_index_list.to_csv(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/data/daily_index.csv')

        pacific_fig, ax = plot_region(daily_anoms.sel(latitude=slice(-30, 30),
                                                      longitude=slice(-180, -80))['sst'], frequency='W', n_periods=3,
                                      subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)),
                                      figsize=(20, 7))
        # monthly anomalies for monitoring
        pacific_fig_monthly, ax = plot_region(merged.sel(latitude=slice(-30, 30),
                                                         longitude=slice(-180, -80))['sst'], frequency='M', n_periods=3,
                                              subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)),
                                              figsize=(20, 7))
        # most recent month
        pacific_fig_monthly, ax = plot_region(merged.sel(latitude=slice(-30, 30),
                                                         longitude=slice(-180, -80))['sst'], frequency='M', n_periods=1,
                                              subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)),
                                              figsize=(8, 8))
        fig.suptitle('Tropical Pacific SST Anomalies')

        nz_daily_fig, ax = plot_region(daily_regions['New Zealand'], frequency='W', n_periods=3,
                                       subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)),
                                       figsize=(6, 12))
        nz_monthly, ax = plot_region(monthly_regions['New Zealand'], frequency='M', n_periods=1,
                                     subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)),
                                     figsize=(6, 12))
        nz_monthly3, ax = plot_region(monthly_regions['New Zealand'], frequency='M', n_periods=3,
                                      subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)),
                                      figsize=(15, 11))
        nz_daily_fig.suptitle('New Zealand SST Anomalies')
fig.show()

# darwin coordinates
soi_test = pd.read_excel(r"/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/data/niwa-soi-latest.xlsx",
                         index_col=0, parse_dates=True)
soi_test2 = soi.to_dataframe()

fig, ax = plt.subplots()
soi_test['SOI'].plot(ax=ax)
soi_test2['msl'].loc["2016":].plot(ax=ax)
fig.show()

fig, ax = plt.subplots(2)
nino34 = merged['sst'].sel(latitude=slice(5, -5),
                           longitude=slice(-170, -120)).mean(["latitude",
                                                              "longitude"]).compute()
merged['sst'].isel(time=-17).plot(ax=ax[0], vmin=-2, vmax=2, cmap='RdBu_r')
# resampled['msl'].isel(time =-1).plot(ax = ax[1])
fig.show()
fig, ax = plt.subplots()
nino34.rolling(time=5).mean().isel(time=slice(-55, None)).plot(ax=ax)
fig.show()
