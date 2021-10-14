import numpy as np
import sys
import pandas as pd
import datetime as dt
import os
import pytz
import datetime
from calendar import monthrange


def load_credentials():
    with open('credentials.txt') as f:
        user_name, password = f.readlines()
        return user_name.split('=')[-1][1:-1], password.split('=')[-1][1:-1]


def determine_date():
    current_date = dt.datetime.now()
    current_month = current_date.month
    print("Current month", current_month)
    current_year = current_date.year
    end_date = current_year
    start_date = 2010
    return start_date, end_date, current_year, current_month, current_date

class GetMullanSeries(object):
    def __init__(self, var_name='TMax', parent_dirs=None, location='Auckland'):
        """
        Obtains the Mullan series (created by Brett Mullan)
        :param var_name: The Variable for which you want to load data for (TMax, TMin, TMean)
        :param parent_dirs: The Directory where (Lincoln_Adjusted_TMean_Anomalies2019.txt) files are stored
        :param location: The Name prefix, e.g (Auckland, Lincoln)
        """
        # Creating the filename string
        if parent_dirs is not None:
            filename = f"{parent_dirs}/{location}_Adjusted_{var_name}_Anomalies2019.txt"
        else:
            filename = f"{location}_Adjusted_{var_name}_Anomalies2019.txt"

        self.location = location
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                       'Oct', 'Nov', 'Dec']
        self.df = pd.read_csv(filename, sep='\s+',
                              skiprows=[0, 1, 2])

        self.df[self.df[self.months] < -8] = np.nan
        self.clim = self.df.iloc[-1]

        # Anomalies

        self.df2 = self.df.copy()
        self.df2[self.months] = self.df2[self.months].iloc[:-1] + self.df2[self.months].iloc[-1]
        self.df = self.df.iloc[:-1]
        self.month_dict = {}
        for i, mon in enumerate(self.months):
            self.month_dict[mon] = i + 1
        self.mullan_anomalies = self.create_continuous_series(self.df)
        self.mullan_series = self.create_continuous_series(self.df2)

    # Could be a static function
    def to_datetime(self, a):
        """

        :param a: A pandas year and month object - only compatible wit the function below
        :return: A pandas to_datetime(function)
        """
        try:
            year = a[0]
            month_ = self.month_dict[a[1]]
            return pd.to_datetime(f"{year}-{month_}-01")
        except:
            return np.nan

    def create_continuous_series(self, df):
        """

        :param df: a Dataframe in a brick like structure (e.g. Year by Month)
        :return: a continous time-series of temperature
        """
        convert = pd.melt(df, id_vars=["Year"])
        convert['datetime'] = convert[['Year', 'variable']].T.apply(self.to_datetime)
        convert = convert.dropna()
        convert.index = convert['datetime']
        convert = convert.sort_index()
        convert[convert['value'] < -5.0] = np.nan
        return convert['value']


class CombineOutputSeries(GetMullanSeries):

    def __init__(self, clidb_series, var_name='TMean', parent_dirs=None, location='Auckland'):
        GetMullanSeries.__init__(self, var_name=var_name, parent_dirs=parent_dirs, location=location)
        self.clidb_series = clidb_series

    @staticmethod
    def create_anomalies_series(a, b):
        frame = pd.DataFrame(dict(value=b, data=a))

        frame['data'][frame['data'].isna() == True] = frame['value'][frame['data'].isna() == True]

        def demean(x):
	        # Stephen Stuarts Modification
            return x - x['value'].loc["1981":"2010"].mean()

        return frame[['data', 'value']].groupby(frame.index.month).apply(demean), frame[['data', 'value']]

    def monthly_regression(self):
        a, b = self.clidb_series, self.mullan_series
        anoms, series = self.create_anomalies_series(a, b)
        return anoms, series


def convert_to_1dp(a):
    try:
        return np.float("%.1f" % a)
    except:
        return np.nan


def covert_series_to_brick(df, output_dirs,output_name ='Anomalies', output_df = False):
    months = ['Jan','Feb','Mar',
              'Apr','May','Jun',
              'Jul','Aug','Sep',
              'Oct','Nov','Dec']
    year = sorted(df.index.year.unique())
    month = sorted(df.index.month.unique())

    for col in df.columns:
        dataframe = pd.DataFrame(columns = month, index = year)
        for years in year:
            arr = df[col][df[col].index.year == years]
            dataframe.loc[years][arr.index.month] = arr.values
        dataframe.columns = months
        dataframe.to_csv(f'{output_dirs}/{output_name}{col}.csv')
    if output_df:
        return dataframe


def create_series(data, station, correction_factor, stat_code, mullan_old_series, station_dict):
    data = data[data.STATS_CODE == stat_code]
    # Subset relevant data
    data.index = data[['STATS_YEAR',
                       'STATS_MONTH']].T.apply(lambda a: pd.to_datetime(f"{a[0]}-{a[1]}-01"))
    # Correctly format the data
    data = data['STATS_VALUE']
    # Convert to a 1.d.p value (for the anomalies)
    data = data.resample('1MS').mean().apply(convert_to_1dp)

    # Ensure the data is sampled in one-month increments (otherwise values are set to nan).

    corrected_station_data = data + correction_factor[station_dict[station]]
    # Applying correction factors from a dictionary above
    # Appending the data to Mullan's old series
    cls = CombineOutputSeries(corrected_station_data, var_name='TMean', location=station_dict[station],
                              parent_dirs=mullan_old_series)

    # Combines the series together
    corrected_anomalies, series = cls.monthly_regression()
    return corrected_anomalies['data'], data, corrected_station_data, series['data']


def make_output_directories(output_dirs):
    """

    :param output_dirs: the output directories
    :return:
    """
    if not os.path.exists(output_dirs):
        os.makedirs(output_dirs)
        os.makedirs(f'{output_dirs}/bricks')
        os.makedirs(f'{output_dirs}/time_series')
    return None
