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
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *
from mjo_funcs import *


years, months, mFMT, yFMT = load_plotting_config__()
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
# f, axes = plot_mjo_cycle(month_before =month_before, current_month = current_month,
#                    previous_month = previous_month,start_month=month_before_s,
#                    middle_month=previous_month_s,
#                    end_month=current_month_s, data_pol=data_pol,
#                    most_recent_month=True)

#f.show()
f2,ax2 = plot_mjo_cycle(month_before =month_before, current_month = current_month,
                   previous_month = previous_month,
                    start_month=month_before_s, middle_month=previous_month_s,
                   end_month=current_month_s, data_pol=data_pol,
                   most_recent_month=False)
label = f"MJO located at Longitude: {data_pol.iloc[-1].lon} in Phase: {'%.0f' % data_pol.iloc[-1].phase}"
ax21= add_reference(ax2, 8, [], top_corner=0.97, separation=0.03,
              data_source="http://www.niwa.co.nz/CPPdata",
              ref="Ref: Madden R. and P. Julian, 1971, N; DOI: 10.1175/1520-0469(1971)028")
ax2 = create_watermark(f2,
                      imagePath='./lib/NIWA_CMYK_Hor.png',
                      label=' ', ax=ax2, alpha=1, loc="lower right")
ax2.text(0.01, 1.02, f"MJO", fontsize=24, fontweight='bold', transform=ax.transAxes)
f2.savefig(f'{output_dirs}/MJO_realtime_plot.png', dpi=200)
#f.savefig(f'{output_dirs}/MJO_realtime_plot_recent.png', dpi=200)
