import urllib.request, urllib.error, urllib.parse
from dateutil import parser as dparser
import pandas as pd
import datetime as dt
import os
import numpy as np
#from IPython import get_ipython
import matplotlib as mpl
from matplotlib import pyplot as plt
import pathlib
from monthdelta import monthdelta
import sys
from datetime import datetime
import os
import matplotlib.dates as mdates
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
clim_start =  1981
clim_end = 2010
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from figure_styles import *


class get_BOM_MSLP:
    def __init__(self, station='tahiti', data_dirs = "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/"):

        self.url = "ftp://ftp.bom.gov.au/anon/home/ncc/www/sco/soi/{}mslp.html".format(station)
        self.station = station
        self.data_dirs = data_dirs
        self.df = self.url_to_dataframe()


    @staticmethod
    def load_url(url):
        """
        param url: reads a BOM url e.g.: 'ftp://ftp.bom.gov.au/anon/home/ncc/www/sco/soi/tahitimslp.html' and
        loads the contents
        """
        req = urllib.request.Request(url)
        r = urllib.request.urlopen(req)
        data = r.read()
        data = data.splitlines()
        return data


    def html_to_dataframe(self,url_data, station):
        """
        param: url_data, reads the output from load_url function, which reads the data in bytes type format.
        output: pandas dataframe
        """

        with open(f'{self.data_dirs}/{station}_text', 'w') as fout:
            # opens a text file and converts the data from html to a text file
            if station == 'tahiti':
                data = url_data[15:-1]
            else:
                data = url_data[14:-1]

            data = [x.decode('utf-8') for x in data]
            data = [x + '\n' for x in data]
            fout.writelines(data)

        data = pd.read_table(f'{self.data_dirs}/{station}_text', sep='\s+', engine='python', na_values='*', index_col=['Year'])

        os.remove(f'{self.data_dirs}/{station}_text')

        return data

    def url_to_dataframe(self):
        bytes_data = self.load_url(self.url)
        dataframe = self.html_to_dataframe(bytes_data, self.station)
        return dataframe


class ComputeSOI:
    def __init__(self, tahitidf,
                 darwindf, clim_start,
                 clim_end, truncate_output_series = "2016/1/1", window =3, min_periods =3):
        """
        param: tahitidf - the class instance of get_BOM_MSLP for tahiti and darwin locations respectively
        param: darwindf - same as above but for darwin
        param: clim_start - the starting point to compute the climatological mean of the indices
        param: clim_end - the end point to compute the climatological mean of the indices
        param: window - the window for compute a smoothed soi index
        """

        self.tahiti_df = tahitidf.df
        self.darwin_df = darwindf.df
        self.clim_start = clim_start
        self.clim_end = clim_end
        self.soi = self.compute_soi()
        self.soi_ts = self.format_soi(self.soi, truncate = truncate_output_series,
                                      window =window, min_periods = min_periods)


    def compute_soi(self):
        tahiti_cli = self.tahiti_df.loc[self.clim_start:self.clim_end, :]
        darwin_cli = self.darwin_df.loc[self.clim_start:self.clim_end, :]

        tahiti_mean = tahiti_cli.mean(0)
        darwin_mean = darwin_cli.mean(0)

        soi = ((self.tahiti_df - tahiti_mean) - (self.darwin_df - darwin_mean)) / ((tahiti_cli - darwin_cli).std(0))
        return soi

    @staticmethod
    def format_soi(soi, truncate = "2016/1/1", window =3, min_periods = 3):
        """
        This function creates a series from a "brick type" monthly dataframe
        param: soi - a brick type series with months as columns and years as the idnex
        """
        ts_soi = pd.DataFrame(soi.stack())
        dates = []
        for i in range(len(ts_soi)):
            dates.append(
                dparser.parse(
                    "{}-{}-1".format(ts_soi.index.get_level_values(0)[i], ts_soi.index.get_level_values(1)[i])))

        ts_soi.index = dates
        ts_soi.columns = ['SOI']
        ts_soi = ts_soi.truncate(before=truncate)
        ts_soi['SOIRM'] = ts_soi.rolling(window=window, min_periods=min_periods, center=True).mean()
        return ts_soi




def check_soi_values(soi):
    # Converts the current date back to the start of the month
    current_date = pd.to_datetime(dt.datetime.utcnow().strftime("%Y-%m-01"))
    latest_update = (current_date - soi.index[-1]).total_seconds()/(3600 * 24)
    return latest_update

def notify_user(lag_from_present):

    if lag_from_present > 65:
        email_title = f"NIWA SOI has not been computed for {lag_from_present}"
        text = "The NIWA SOI did not run successful please check"
        rcode = os.popen(
            'export LC_CTYPE="en_US.UTF-8" && mail -s "{}" Neelesh.Rampal@niwa.co.nz'.format(
                email_title), 'w').write(text)
        return False

    else:
        return True

def compute_soi(tahitidf, darwindf):
    tahiti_cli = tahitidf.df.loc[clim_start:clim_end,:]
    darwin_cli = darwindf.df.loc[clim_start:clim_end,:]

    tahiti_mean = tahiti_cli.mean(0)
    darwin_mean = darwin_cli.mean(0)
    ### ==============================================================================================================

    ### ==============================================================================================================
    ### Step 3: calculate the SOI
    soi = ((tahitidf.df - tahiti_mean) - (darwindf.df - darwin_mean)) / ((tahiti_cli -  darwin_cli).std(0))
    ts_soi = pd.DataFrame(soi.stack())

    dates = []
    for i in range(len(ts_soi)):
        dates.append(dparser.parse("{}-{}-1".format(ts_soi.index.get_level_values(0)[i], ts_soi.index.get_level_values(1)[i])))

    ts_soi.index = dates
    ts_soi.columns = ['soi']
    ts_soi = ts_soi.loc['1950':]
    ts_soi.loc[:,'soi3m'] = ts_soi.rolling(window=3, min_periods=3).mean()
    return ts_soi, dates, soi


def handle_figure_update_mssg(output_path_fig, new_fig_created):
    if new_fig_created:
        email_title = f"Updated NIWA SOI"
        text = "Here is the latest run of the NIWA SOI"
        rcode = os.popen(
            'export LC_CTYPE="en_US.UTF-8" && mail -a {} -s "{}" Neelesh.Rampal@niwa.co.nz'.format(output_path_fig,
                email_title), 'w').write(text)
    else:
        email_title = f"NIWA has already run successful and does not need to be updated"
        text = "Here is the latest run of the NIWA SOI"
        rcode = os.popen(
            'export LC_CTYPE="en_US.UTF-8" && mail -a {} -s "{}" Neelesh.Rampal@niwa.co.nz'.format(output_path_fig,
                email_title), 'w').write(text)


def load_nino(url ='http://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii', clim_start = clim_start,
              clim_end = clim_end):
    nino = pd.read_csv(url, sep='\s+', engine='python')
    nino = nino[['YR', 'MON', 'NINO3.4']]
    nino.loc[:, 'DAY'] = 1
    nino_clim = nino.copy()
    nino_clim.index = nino_clim.YR
    nino_clim = nino_clim.loc[clim_start:clim_end, :]
    nino_clim = nino_clim.groupby(nino_clim.MON).mean()
    nino.index = nino[['YR', 'MON', 'DAY']].apply(lambda d: datetime(*d), axis=1)

    def demean(x):
        return x - x.loc[str(clim_start):str(clim_end)].mean()

    nino['anoms'] = nino.groupby(nino.MON)[['NINO3.4']].transform(demean)
    ninos = nino[['anoms']]
    ninos.columns = ['NINO34']
    nino['anoms5m'] = nino['anoms'].rolling(window=5, min_periods=5).mean()
    return nino_clim, nino, ninos

def zscore(x, clim_start, clim_end):
    return (x - x.loc[str(clim_start):str(clim_end)].mean()) / x.loc[str(clim_start):str(clim_end)].std()