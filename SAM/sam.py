
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

import pandas as pd

url = 'https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/aao/monthly.aao.index.b79.current.ascii.table'
sam = pd.read_table(url, sep=r"\s+")
sam = sam.stack()
sam.index = pd.date_range(start='1979-01-31', freq='M', periods=len(sam))
sam = sam.to_frame(name='SAM')
number_of_lagged_times_in_plot =48
dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=sam.iloc[-number_of_lagged_times_in_plot:],
                                                        col1='SAM', col2='SAM')

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
fig.savefig(f'./SAM/figures/SAM_index.png',dpi=300)
sam.to_csv(f'./SAM/data/SAM.csv')
sam.to_excel(f'./SAM/data/SAM.csv')

