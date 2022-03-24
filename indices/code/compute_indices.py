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
os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *

warnings.simplefilter(action="ignore", category=FutureWarning)
years, months, mFMT, yFMT = load_plotting_config__()
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/'
# import s
clim_start = 1981
clim_end = 2010
nino_start = "2016"

if __name__ == "__main__":



    # %%
    today = datetime.utcnow() - timedelta(15)
    url = 'https://data.longpaddock.qld.gov.au/SeasonalClimateOutlook/SouthernOscillationIndex/SOIDataFiles/DailySOI1933-1992Base.txt'
    r = requests.get(url)

    if r.status_code != 200:
        print(f"The URL cannot be accessed for some reason, please check the URL:\n {url}")
    os.environ['HTTP_PROXY'] = ''

    soi = pd.read_csv(url, delim_whitespace=True)
    index = [datetime(int(year), 1, 1) + timedelta(int(day) - 1) for year, day in soi.loc[:, ['Year', 'Day']].values]
    soi.index = index
    # Save the SOI
    soi.to_csv(f'{output_dirs}/data/daily_soi.csv')
    soi.to_excel(f'{output_dirs}/data/daily_soi.xlsx')
    mslp = soi.copy()
    soi = soi.loc[:, ['SOI']]
    soi['soirm1'] = soi[['SOI']].rolling(window=30).mean()
    soi['soirm3'] = soi[['SOI']].rolling(window=90).mean()
    # Keep the last two years
    soi = soi.loc[str(soi.index.year[-1] - 2):, :]

    # %%
    # Keeping the last three months of code
    dates, widths, soi_, soim = format_series_for_bar_plot__(ts_soi=soi.iloc[-90:]/10.0, col1='soirm1', col2='soirm3', weekly='daily')
    widths[-1] = widths[-2]
    fig, ax, output_directory,new_fig_created,textBm, textBs= plot_data(dates, soi_, widths,
                                                             soim, months,
                                         output_path=f'{output_dirs}',
                                         cei=True, var_name=f'NIWA SOI (last 3 months)', var_2='SOI 3-month', title=False, label_bool = None,
                                                                        ylim=(-2,2), period2 =30, period1 = 1, periodicity ='D')
    text = "%s to %s = %+3.1f" % (soi.index[-90].strftime("%b %d %Y"),
                                  soi.index[-1].strftime("%b %d %Y"), soi.iloc[-1, 1]/10.0)

    add_reference(ax, 12, [textBm, textBs, text], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref=f"Ref: Troup, 1965; DOI:10.1002/qj.49709139009")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=10))
    ax.text(0.01, 0.97 - 4 * 0.03, text, fontweight='bold', fontsize=12,
            transform=ax.transAxes)
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(f'{output_dirs}figures/SOI_LP_realtime_plot.png', dpi=200)

    # loading the various nino indices

    url = 'http://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii'
    nino = pd.read_csv(url, sep='\s+', engine='python')
    nino['year'] = nino['YR']
    nino['month'] = nino['MON']
    nino['day'] = 1
    nino.index = pd.to_datetime(nino[['year', 'month', 'day']])
    nino1 = nino.filter(regex="NINO").to_xarray()
    clim = nino1.groupby(nino1.index.dt.month).apply(lambda a: a.sel(index=slice("1991", "2020")).mean("index"))
    anoms = nino1.groupby(nino1.index.dt.month) - clim
    anoms = anoms.to_pandas().drop(["month"], axis =1)
    anoms.to_csv(f'{output_dirs}/data/monthly_nino_index.csv')
    anoms.to_excel(f'{output_dirs}/data/monthly_nino_index.xlsx')
    for nino in ['NINO1+2', 'NINO3', 'NINO4', 'NINO3.4']:
        data = anoms.loc[nino_start:, [nino]]
        try:
            lastmonth = data.loc[today.strftime("%Y-%m")].mean()
        except KeyError:
            print("Midmonth Update")
            today = datetime.utcnow() - timedelta(31)
            lastmonth = data.loc[today.strftime("%Y-%m")].mean()

        dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=data[-30:], col1=nino, col2=nino, weekly=False)
        widths[-1] = widths[-2]
        fig, ax, output_directory, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                                               soim, months,
                                                                               output_path=f'{output_dirs}',
                                                                               cei=True,
                                                                               var_name=f'{nino} Index',
                                                                               var_2='SOI 3-month', title=False,
                                                                               label_bool=None,
                                                                               ylim=(-3, 3), period2=3, period1=1,
                                                                               periodicity='M')
        ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
        add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
                      data_source="http://www.niwa.co.nz/CPPdata",
                      ref=f"Ref: Rasmussen and Carpenter (1982); DOI:10.1175/1520-0493")
        fig.savefig(f'{output_dirs}/figures/NINO{nino}_realtime_plot.png', dpi=200, bbox_inches='tight')
            #fig.show()



    # files_list = glob.glob(f'{output_dirs}/figures/*.png')
    # base_string = 'export LC_CTYPE="en_US.UTF-8" && mail'
    # for file in files_list:
    #     base_string+=f' -a {file}'
    # email_title = "Nino Indices"
    # text = "Automation Sent"
    # base_string+= ' -s "{}" Neelesh.Rampal@niwa.co.nz,Ben.Noll@niwa.co.nz,Tristan.Meyers@niwa.co.nz'.format(email_title)
    # rcode = os.popen(base_string,'w').write(text)
print("code execute succesfully")





