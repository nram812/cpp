import xarray as xr
from dask.diagnostics import ProgressBar
import matplotlib.pyplot as plt
import pandas as pd
# M1 = HOBA - CHAT

# Adding the BZ1 stations, and so on.
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
# Load the coordinates for each of the sites
# defining the coordinate list
number_of_lagged_times_in_plot = 48

# added 360 to coordinates
coords_list ={}
coords_list['hobart_coords'] = (-42.880554, 147.324997)
coords_list['auckland_coords'] = (-36.850109, 174.767700)
coords_list['chatham_coords'] = (-43.8923, -176.5240 + 360 )
coords_list['chch_coords'] = (-43.525650,172.639847)
coords_list['cai_coords'] = (-52.55, 169.11 )
coords_list['darwin_coords'] = (-12.433, 130.867)
coords_list['adelaide_coords'] = (-34.93, 138.58)
coords_list['syndey_coords'] = (-33.867, 151.2)
coords_list['wellington_coords'] = (-41.28, 174.76)
coords_list['hokita_coords'] = (-42.71, 170.95)
coords_list['raoul_island'] = (-29.25, 177.916)
coords_list['apia_coords'] = (-13.8333, -171.7667 + 360)
coords_list['invercargill_coords'] = ( -46.4250 , 168.3100)
#coords_list['stanley_coords'] = (-52.0, -58 + 360)
coords_list['new_plymouth_coords'] = (-39.05, 174.07)
coords_list['gisborne_coords'] = (-38.66, 178.017)

# Plotting limits these are the extents for the plots
ylims ={}
ylims['M1'] = (-130,130)
ylims['M2'] = (-90,90)
ylims['M3'] = (-80,80)
ylims['Z1'] = (-80,80)
ylims['Z2'] = (-80,80)
ylims['Z3'] = (-80,80)
ylims['Z4'] = (-130,130)
ylims['Z5'] = (-80,80)
ylims['ZN'] = (-60,60)
ylims['ZS'] = (-60,60)
ylims['SET'] = (-60,60)
ylims['TPI'] = (-130,130)
ylims['MZ1'] = (-50,50)
ylims['MZ2'] = (-80,80)
ylims['MZ3'] = (-80,80)
ylims['MZ4'] = (-20,20)

### Code begins

# loading the downloaded dataset
# Points are directly on the boundary of the data
complete_dset = xr.open_dataset(f'{path}/monthly_mean_mslp.nc', chunks={"time":1000})
# complete_dset['longitude'] = complete_dset.longitude.where(complete_dset.longitude < 180.0
files = glob.glob(f"{path}/single-levels/*/*.nc")
files = sorted(files)
with ProgressBar():
    load_downloaded_dset = xr.open_mfdataset(files, combine ="nested", parallel=True)

load_downloaded_dset['longitude'] = load_downloaded_dset.longitude.where(load_downloaded_dset.longitude > 0.0,
                                                                         load_downloaded_dset.longitude  + 360)
load_downloaded_dset = \
    load_downloaded_dset.reindex(longitude=sorted(load_downloaded_dset.longitude.values))
load_downloaded_dset = load_downloaded_dset.interp_like(complete_dset['msl'].isel(time =0))
resampled = load_downloaded_dset.resample(time = '1MS').mean()
with ProgressBar():
    resampled = resampled.load()

# I've checked that the data matches between the daily and the monthly

def subtract_clim(df, period = ["1961","1990"]):
    """

    :param df: a dataset with time dimension time
    :param period: the climatological period to compute the mean over
    :return:
    """
    return df.groupby(df.time.dt.month).apply(lambda a: a- a.sel(time = slice(period[0], period[1])).mean("time"))


def create_trenbert(df,
                    coords_list = {}):
    output_clim = {}
    for key, coords in coords_list.items():
        pressure = (df['msl'].interp(latitude=coords[0], longitude=coords[1], method='linear'))
        pressure = subtract_clim(pressure)
        output_clim[key] = pressure
    return output_clim


# need to subtract the 1981 to 2021 normal period from

with ProgressBar():
    merged = xr.merge([resampled['msl'],  complete_dset.sel(time = slice(None, "2021-04-01")).interp_like(resampled.isel(time=0), method='nearest')])
    merged = merged.drop("expver")
    climatologies = create_trenbert(merged, coords_list)
    # lets now compute all the trenberth indices
    z1 = (climatologies['auckland_coords'] - climatologies['chch_coords']).compute() // 10.0
    z2 = (climatologies['chch_coords'] - climatologies['cai_coords']).compute() // 10.0
    z3 = (climatologies['auckland_coords'] - climatologies['invercargill_coords']).compute() // 10.0
    z4 = (climatologies['raoul_island'] - climatologies['chatham_coords']).compute() // 10.0
    z5 = (climatologies['syndey_coords'] - climatologies['hobart_coords']).compute() // 10.0
    #
    m1 = (climatologies['hobart_coords'] - climatologies['chatham_coords']).compute() // 10.0
    m2 = (climatologies['hokita_coords'] - climatologies['chatham_coords']).compute() // 10.0
    m3 = (climatologies['hobart_coords'] - climatologies['hokita_coords']).compute() // 10.0

    mz1 = (climatologies['gisborne_coords'] - climatologies['hokita_coords']).compute() // 10.0
    mz2 = (climatologies['gisborne_coords'] - climatologies['invercargill_coords']).compute() // 10.0
    mz3 = (climatologies['new_plymouth_coords'] - climatologies['chatham_coords']).compute() // 10.0
    mz4 = (climatologies['auckland_coords'] - climatologies['new_plymouth_coords']).compute() // 10.0
    set1 = (climatologies['raoul_island'] - climatologies['apia_coords']).compute() // 10.0
    #tpi = (climatologies['hobart_coords'] - climatologies['stanley_coords']).compute() // 10.0
    zn = (climatologies['auckland_coords'] - climatologies['wellington_coords']).compute() // 10.0
    zs = (climatologies['wellington_coords'] - climatologies['invercargill_coords']).compute() // 10.0


def rename_index(index, name = ''):
    """

    :param index: an instance of an interpolated index as shown above
    :param name:  the renaming name
    :return:
    """
    return index.to_dataset().rename({"msl":name}).to_dataframe()
# creating all the indices in one go
# removed the TPI index from here

merged_index = pd.concat([rename_index(z1, "Z1"),
                          rename_index(z2, "Z2"),
                          rename_index(z3, "Z3"),
                          rename_index(z4, "Z4"),
                          rename_index(z5, "Z5"),
                          rename_index(m1, "M1"),
                          rename_index(m2, "M2"),
                          rename_index(m3, "M3"),
                          rename_index(mz1, "MZ1"),
                          rename_index(mz2, "MZ2"),
                          rename_index(mz3, "MZ3"),
                          rename_index(mz4, "MZ4"),
                          rename_index(zn, "ZN"),
                          rename_index(zs, "ZS"),
                          rename_index(set1, "SET")], axis=1)
# Load the plotting configurations

output_file_dirs = f'./trenberth_figures'
merged_index.to_csv(f'./trenberth_figures/data/updated_trenberth_index.csv')
merged_index.to_excel(f'./trenberth_figures/data/updated_trenberth_index.xlsx')
# saving the index

for index in merged_index.columns:
    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=merged_index.iloc[-number_of_lagged_times_in_plot:],
                                                            col1=index, col2='Z1')

    fig, ax, __, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                             soim, months,
                                                             output_path=f'./CEI/figures',
                                                             cei=True, var_name=f'NIWA {index} Index',
                                                             var_2='', title=False, label_bool=None,
                                                             period1=1, period2=3, periodicity='M', ylim=ylims[index],
                                                             figsize=(14, 10))
    add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref="Ref: Trenberth, Kevin E, 1976; DOI: 10.1002/qj.49710243106")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
    ax.grid(False)
    #fig.show()
    fig.savefig(f'{output_file_dirs}/figures/{index}_index.png')



    #fig.savefig(output_file_dirs, dpi=300)

    #handle_figure_update_mssg(output_file_dirs, True)

#m11['msl'] = np.int(m11['msl'])/10.0
merged_index = pd.read_csv(f'./trenberth_figures/data/updated_trenberth_index.csv',
                           index_col =0, parse_dates = True)
