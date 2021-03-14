import warnings
import os
import sys
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/lib')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/plot-style')
from niwa_soi_funcs import *
from plot_style import *

# Load all neccessary functions from home directory
years, months, mFMT, yFMT = load_plotting_config__()
warnings.filterwarnings('ignore', category=FutureWarning)

# Define the climatological period to calculate the soi
clim_start = 1941
clim_end = 2010

# Define the climatological period
tahitidf = get_BOM_MSLP(station='tahiti')
darwindf = get_BOM_MSLP(station='darwin')
# Load the tahiti and darwin series of data
soi_cls = ComputeSOI(tahitidf, darwindf, clim_start = clim_start, clim_end = clim_end)
soi_ = soi_cls.soi_ts

soi_.to_excel('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/data/niwa-soi-latest.xlsx')
# Check if new data has been recently added, run the script if new data has been added
time_lag = check_soi_values(soi_)
if notify_user(time_lag):
    # Compute the soi from the two series
    years, months, mFMT, yFMT = load_plotting_config__()
    # Prepare the data for plotting a bar grap

    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=soi_.iloc[-48:], col1='SOI', col2='SOIRM')
    output_dirs = r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi'
    fig, ax, output_dirs, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                                      soim, months, years,
                                                                      mFMT, yFMT,
                                                                      output_path=f'{output_dirs}/figures',
                                                                      cei=True, var_name='NIWA Southern Oscillation Index (NIWA SOI)',
                                                                      var_2='SOI 3-month', title=False, label_bool=None)
    #ax = add_categories(ax)
    separation = 0.03
    top_corner = 0.97
    ax.grid(False)
    ax.text(0.01, top_corner, f"Ref: Troup, 1965; DOI:10.1002/qj.49709139009", fontsize=12, fontweight='normal',
            transform=ax.transAxes)
    ax.text(0.01, top_corner - separation, f"Data Sources: See http://www.niwa.co.nz/CPPdata", fontsize=12,
            fontweight='normal', transform=ax.transAxes)
    ax.text(0.01, top_corner - 2 * separation, "{}".format(textBm), fontweight='bold', fontsize=12,
            transform=ax.transAxes)
    ax.text(0.01, top_corner - 3 * separation, "{}".format(textBs), fontweight='bold', fontsize=12,
            transform=ax.transAxes)
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))

    # Handle the updates and the send an email out
    handle_figure_update_mssg(output_path_fig, new_fig_created)
