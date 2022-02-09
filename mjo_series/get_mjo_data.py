import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import pyplot as plt
from dateparser import parse
import sys

sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/')
import urllib.request, urllib.error, urllib.parse
from dateutil import parser as dparser
import pandas as pd
import datetime as dt
import os
import numpy as np
from IPython import get_ipython
import matplotlib as mpl
from matplotlib import pyplot as plt
import pathlib
from monthdelta import monthdelta
import sys

from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from cycler import cycler
import os
os.chdir('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
sys.path.append(r'./lib')

from cei_funcs import *
from mjo_funcs import *


# %%
current_month_s = parse('0 months ago')
previous_month_s = parse('1 months ago')
month_before_s = parse('2 months ago')

# %%
current_month = current_month_s.strftime("%B")
previous_month = previous_month_s.strftime("%B")
month_before = month_before_s.strftime("%B")
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/mjo_series/data'
# ### this is where the Wheeler and Hendon (2004) realtime RMM index lives, and what it looks like

data, data_pol = read_url(month_before_s = month_before_s)
data.to_csv('./data/mjo_data/phase_historical.csv')
data_pol.to_csv('./data/mjo_data/phase_recent.csv')
data.to_excel('./data/mjo_data/phase_historical.xlsx')
data_pol.to_excel('./data/mjo_data/phase_recent.xlsx')
