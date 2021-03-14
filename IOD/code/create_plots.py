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
register_matplotlib_converters()
import os
os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *
import os


# Listing the ersst files that are required to be processed
start_year = 1950
years, months, mFMT, yFMT = load_plotting_config__()
filelist = glob.glob(r'./IOD/data/ersst.v5.??????.nc',
                     recursive = True)
times = [pd.to_datetime(file.split('/')[-1], format = 'ersst.v5.%Y%m.nc')
         for file in filelist]
# Loading the times of the files to be processed - as there are sometime issues with creating them

output_dirs = './IOD/data'
output_f_dirs = './IOD/figures'
# Note output_f_dirs is for creating figures
dset, sst_anoms = create_ersst_nc(filelist, times, output_dirs)




# %%
if __name__ == "__main__":
    #f, ax = plotting_sst_pattern(sst_anoms, figsize =(15,15))
    IOD = create_iod_series(sst_anoms)

    f, ax = plt.subplots(figsize=(12,6))
    ax.fill_between(IOD.index,IOD.IOD.values, 0, (IOD.IOD.values>=0), color='steelblue', alpha=.9, interpolate=True)
    create_watermark(f,
                     label=None, ax=ax, alpha=1, loc="lower right")
    ax.fill_between(IOD.index,IOD.IOD.values, 0, (IOD.IOD.values<0), color='coral', alpha=.9, interpolate=True)
    ax.plot(IOD.index, IOD.IOD.values, c='k', lw=0.2)
    ax.grid('on')
    ax.axhline(0,c='0.4',lw=0.5)
    ax.set_xlabel('Year')
    ax.set_ylabel('IOD')
    f.suptitle(f'Indian Ocean Dipole (IOD) \n'
               f'{IOD.index[-1].strftime("%Y-%B")} value: {"%.2f" % IOD["IOD"].values[-1]}', fontsize=14);
    f.savefig(f'{output_f_dirs}/IOD_series_plot.png', dpi =300)
    f.show()
    IOD.to_csv(f'{output_dirs}/Monthly_IOD.csv')
    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=IOD.iloc[-48:], col1 ='IOD', col2 = 'IOD', weekly = False)
    # fig, ax, output_dirs, new_fig_created,textBm, textBs = plot_data(dates, soi, widths,
    #                                                   soim, months, years,
    #                                                   mFMT, yFMT,
    #                                                   output_path=f'{output_f_dirs}',
    #                                                   cei = True, var_name ='Indian Ocean Dipole (IOD)', var_2 = 'SOI 3-month', title = False, label_bool = None,
    #                                                                  ylim = (-7,7))
    fig, ax, output_directory,new_fig_created,textBm, textBs= plot_data(dates, soi, widths,
                                                             soim, months,
                                         output_path=f'{output_f_dirs}',
                                         cei=True, var_name='Indian Ocean Dipole (IOD)', var_2='SOI 3-month', title=False, label_bool = None,
                                                                        ylim=(-6,6), period2 =3, period1 = 1, periodicity ='M')
    separation = 0.03
    top_corner = 0.97
    ax.grid(False)
    add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref=f"Ref: Saji et al., 1999; DOI:10.1038/43854")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
    fig.show()
    fig.savefig(f'{output_f_dirs}/IOD_series_plot_recent1.png', dpi =300)
    
    files_list = glob.glob(f'{output_f_dirs}/IOD_series_plot_recent1*.png')
    base_string = 'export LC_CTYPE="en_US.UTF-8" && mail'
    for file in files_list:
        base_string+=f' -a {file}'
    email_title = "IOD Index"
    text = "Automation Sent"
    base_string+= ' -s "{}" Neelesh.Rampal@niwa.co.nz,Ben.Noll@niwa.co.nz,Tristan.Meyers@niwa.co.nz'.format(email_title)
    rcode = os.popen(base_string,'w').write(text)
