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


if __name__ == "__main__":
    # import s
    clim_start = 1981
    clim_end = 2010

    output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/'


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
    mslp = soi.copy()
    soi = soi.loc[:, ['SOI']]
    soi['soirm1'] = soi[['SOI']].rolling(window=30).mean()
    soi['soirm3'] = soi[['SOI']].rolling(window=90).mean()
    # Keep the last two years
    soi = soi.loc[str(soi.index.year[-1] - 2):, :]

    # %%
    # Keeping the last three months of code
    dates, widths, soi_, soim = format_series_for_bar_plot__(ts_soi=soi.iloc[-90:], col1='soirm1', col2='soirm3', weekly='daily')
    widths[-1] = widths[-2]
    fig, ax, output_directory,new_fig_created,textBm, textBs= plot_data(dates, soi_, widths,
                                                             soim, months,
                                         output_path=f'{output_dirs}',
                                         cei=True, var_name=f'NIWA SOI (last 3 months)', var_2='SOI 3-month', title=False, label_bool = None,
                                                                        ylim=(-30,30), period2 =30, period1 = 1, periodicity ='D')
    text = "%s to %s = %+3.1f" % (soi.index[-90].strftime("%b %d %Y"), soi.index[-1].strftime("%b %d %Y"), soi.iloc[-1, 1])

    add_reference(ax, 12, [textBm, textBs, text], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref=f"Ref: Troup, 1965; DOI:10.1002/qj.49709139009")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
    ax.text(0.01, 0.97 - 4 * 0.03, text, fontweight='bold', fontsize=12,
            transform=ax.transAxes)
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(f'{output_dirs}figures/SOI_LP_realtime_plot.png', dpi=200)

    for nino in ["3.4", "3", "4", "1", "2"]:

        print("processing NINO{}".format(nino))

        url = "http://www.bom.gov.au/climate/enso/nino_%s.txt" % (nino)

        r = requests.get(url)

        if r.status_code != 200:
            print(f"something went wrong with accessing the URL {url}")

        else:

            data = pd.read_table(BytesIO(r.content), sep=',', header=None, index_col=1, parse_dates=True,
                                 names=['iDate', 'SST'])
            data.to_csv(f'{output_dirs}/data/NINO_{nino}.csv')

            data = data.loc['2016':, :]
            lastmonth = data.loc[today.strftime("%Y-%m"), 'SST'].mean()

            dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=data[-20:], col1='SST', col2='SST', weekly=True)
            widths[-1] = widths[-2]
            fig, ax, output_directory, new_fig_created, textBm, textBs = plot_data(dates, soi, widths,
                                                                                   soim, months,
                                                                                   output_path=f'{output_dirs}',
                                                                                   cei=True,
                                                                                   var_name=f'NIWA Nino {nino} Index',
                                                                                   var_2='SOI 3-month', title=False,
                                                                                   label_bool=None,
                                                                                   ylim=(-2, 2), period2=2, period1=1,
                                                                                   periodicity='D')
            ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))

            add_reference(ax, 12, ['Week ending {} : {}'.format(data.index[-1].strftime("%B %d %Y"),data.iloc[-1, -1]),
                                   f'Month ending {data.index[-1].strftime("%B %d %Y")} : {"%.2f" % lastmonth}'], top_corner=0.97, separation=0.03,
                          data_source="http://www.niwa.co.nz/CPPdata",
                          ref=f"Ref: Troup, 1965; DOI:10.1002/qj.49709139009")
            output_dirs = r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices'
            fig.savefig(f'{output_dirs}/figures/NINO{nino}_realtime_plot.png', dpi=200)
            #fig.show()



    files_list = glob.glob(f'{output_dirs}/figures/*.png')
    base_string = 'export LC_CTYPE="en_US.UTF-8" && mail'
    for file in files_list:
        base_string+=f' -a {file}'
    email_title = "Nino Indices"
    text = "Automation Sent"
    base_string+= ' -s "{}" Neelesh.Rampal@niwa.co.nz,Ben.Noll@niwa.co.nz,Tristan.Meyers@niwa.co.nz'.format(email_title)
    rcode = os.popen(base_string,'w').write(text)






