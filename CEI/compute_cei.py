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
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *

# Load the plotting configurations
years, months, mFMT, yFMT = load_plotting_config__()
output_file_dirs = f'./CEI/figures/CEI_series_2018_present.png'
clim_start = 1981
clim_end = 2010


def organize_cei(clim_start=clim_start, clim_end=clim_end):
    """
    For a given climatology this function calculates the CEI

    :param clim_start: starting climatologcial

    :param clim_end: ending climatologiay
    :return:
    """
    # --- Here is the analysis for the CEI ---
    tahitidf = get_BOM_MSLP(station='tahiti')
    darwindf = get_BOM_MSLP(station='darwin')
    # Process the soi and other fields
    ts_soi, dates, soi = compute_soi(tahitidf, darwindf)
    ts_soi.columns = ['soi', 'soi3m']
    nino_clim, nino, ninos = load_nino()
    data = ts_soi[['soi3m']]
    data['nino5m'] = nino.loc[:, 'anoms5m'].copy()
    dates, data = create_CEI(data, clim_start, clim_end)
    data = create_categories(data)
    data['Year'] = data.index.year
    data['Month'] = data.index.month
    data = data[['Year', 'Month', 'soi3m', 'nino5m', 'CEI', 'category', 'code']]
    datas = data  # .loc['2018':,:]

    return data, datas

if __name__ == "__main__":

    data, datas = organize_cei(clim_start, clim_end)

    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=datas.iloc[-48:], col1='CEI', col2='soi3m')

    fig, ax, __, new_fig_created,textBm, textBs = plot_data(dates, soi, widths,
                                         soim, months,
                                         output_path=f'./CEI/figures',
                                         cei=True, var_name='Coupled ENSO Index (CEI)', var_2='SOI 3-month', title = False, label_bool = None,
                                                            period1 =1, period2 =3, periodicity = 'M')


    ax, data = add_categories(ax, data)
    add_reference(ax,12,[textBm, textBs], top_corner=0.97, separation = 0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref="Ref: Gergis & Fowler, 2005; DOI: 10.1002/joc.1202")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
    fig.tight_layout()
    #fig.show()
    datas.to_csv(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/CEI/data/new_CEI.csv')

    fig.savefig(output_file_dirs,dpi =300)

    #handle_figure_update_mssg(output_file_dirs, True)
