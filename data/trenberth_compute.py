import xarray as xr
from dask.diagnostics import ProgressBar
import matplotlib.pyplot as plt
import pandas as pd
# M1 = HOBA - CHAT
import numpy as np
import sys
import pandas as pd
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import requests
import urllib.request, urllib.error, urllib.parse
from dateutil import parser as dparser
from datetime import datetime, timedelta
import subprocess
from datetime import datetime
import os

# Remove the grid and fix the axis labels

os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
# os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *
years, months, mFMT, yFMT = load_plotting_config__()
# INDEX: Z1 = AUCK - CHCH
hobart_coords = (-42.880554, 147.324997)
auckland_coords = (-36.850109, 174.767700) #albert park
chatham_coords = ( -43.8923, 176.5240)
chch_coords = (-43.525650,172.639847)
path = r"/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/"
#os.chdir(path)

# loading the historical trenberth monthly
complete_dset = xr.open_dataset(f"{path}monthly_single_levels_era5_complete.nc", chunks={"time":1})

complete_dset['longitude'] = np.arange(0,180, 0.25).tolist() + np.arange(-180,0, 0.25).tolist()
complete_dset = complete_dset.reindex(longitude = np.arange(-180,180,0.25))

# complete dset ends on 2021-04-1
load_downloaded_dset = xr.open_mfdataset(f"{path}/single-levels/*/*.nc", parallel = True)
resampled = load_downloaded_dset.resample(time = '1MS').mean()
#resampled = bounds(resampled)
# load daily dataset of trenberth


# merge_with old dataset
def subtract_clim(df, period = ["1961","1990"]):
    return df.groupby(df.time.dt.month).apply(lambda a: a- a.sel(time = slice(period[0], period[1])).mean("time"))


def create_trenbert(df, auckland_coords, hobart_coords, chatham_coords, chch_coords):
    hobart_pressure = (df['msl'].interp(latitude =hobart_coords[0], longitude = hobart_coords[1], method='linear'))
    chatham_pressure = df['msl'].interp(latitude =chatham_coords[0], longitude = chatham_coords[1], method='linear')
    auckland = df['msl'].interp(latitude =auckland_coords[0], longitude = auckland_coords[1], method='linear')
    chch = df['msl'].interp(latitude =chch_coords[0], longitude = chch_coords[1], method='linear')
    return subtract_clim(hobart_pressure), subtract_clim(chatham_pressure), subtract_clim(auckland), subtract_clim(chch)


# need to subtract the 1981 to 2021 normal period from

with ProgressBar():
    merged = xr.merge([resampled, complete_dset.interp_like(resampled.isel(time=0), method='nearest')])
    #merged = subtract_clim(merged)
    hobart, chatham, auckland,chch = create_trenbert(merged,auckland_coords, hobart_coords, chatham_coords, chch_coords)
    m11 = (hobart - chatham).compute()//10.0
    z11 = (auckland - chch).compute()//10.0

# Load the plotting configurations

output_file_dirs = f'./trenberth_figures'
merged_index = pd.concat([m11.to_dataset().rename({"msl":"M1"}).to_dataframe(), z11.to_dataset().rename({"msl":"Z1"}).to_dataframe(),], axis=1)

if __name__ == "__main__":

    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=merged_index.iloc[-48:], col1='M1', col2='Z1')
    merged_index.to_csv(f'./trenberth_figures/data/updated_trenberth_index.csv')
    fig, ax, __, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                             soim, months,
                                                             output_path=f'./CEI/figures',
                                                             cei=True, var_name='NIWA M1 Index',
                                                             var_2='', title=False, label_bool=None,
                                                             period1=1, period2=3, periodicity='M', ylim = (-130,130),
                                                             figsize = (14,10))
    add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref="Ref: Trenberth, Kevin E, 1976; DOI: 10.1002/qj.49710243106")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
    ax.grid(False)
    fig.savefig(f'{output_file_dirs}/figures/M1_index.png')

    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=merged_index.iloc[-48:], col1='Z1', col2='M1')
    fig2, ax2, __, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                             soim, months,
                                                             output_path=f'./CEI/figures',
                                                             cei=True, var_name='NIWA Z1 Index',
                                                             var_2='', title=False, label_bool=None,
                                                             period1=1, period2=3, periodicity='M', ylim = (-80,80),
                                                             figsize = (14,10))
    ax2.grid(False)
    add_reference(ax2, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref="Ref: Trenberth, Kevin E, 1976; DOI: 10.1002/qj.49710243106")
    ax2.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))

    #fig2.tight_layout()
    fig2.savefig(f'{output_file_dirs}/figures/Z1_index.png', dpi =300)

    #fig.savefig(output_file_dirs, dpi=300)

    #handle_figure_update_mssg(output_file_dirs, True)

#m11['msl'] = np.int(m11['msl'])/10.0

