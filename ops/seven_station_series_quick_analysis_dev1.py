import pandas as pd
import numpy as np
dirs = r'C:\Users\rampaln\OneDrive - NIWA\Research Projects\Temperature Anomalies\seven_station\seven_station_series'
import pandas as pd
from scipy.stats import linregress

# Some stations contain data to 1943, while other only contain temperature data to 2001 /or 1999
# Brett likely has some homogenisation steps between here.
# Confirm what the adjustments in temperature actually are.

# We can compute an automated email on Maui - that enables us to do this.


# This is potentially one of the adjustments.
#0.00, -0.28, -0.06, 0.00, 0.00, 0.00, 0.00

class LoadRegression(object):
    def __init__(self, var_name = 'TMax', parent_dirs = dirs, location= 'Auckland'):
        """

        :param var_name: The Variable for which you want to load data for (TMax, TMin, TMean)
        :param parent_dirs: The Directory where (Lincoln_Adjusted_TMean_Anomalies2019.txt) files are stored
        :param location: The Name prefix, e.g (Auckland, Lincoln)
        """
        # Creating the filename string
        filename = f"{parent_dirs}/{location}_Adjusted_{var_name}_Anomalies2019.txt"
        self.location = location
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                  'Oct', 'Nov', 'Dec']
        self.df = pd.read_csv(filename, sep='\s+', skiprows=[0, 1, 2])
        self.df[self.df[self.months] < -8] = np.nan
        self.clim = self.df.iloc[-1]


        # Anomalies

        self.df2 = self.df.copy()
        self.df2[self.months] = self.df2[self.months].iloc[:-1] +self.df2[self.months].iloc[-1]
        self.df = self.df.iloc[:-1]
        self.month_dict = {}
        for i, mon in enumerate(self.months):
            self.month_dict[mon] = i + 1
        self.mullan_anomalies = self.create_continous_series(self.df)
        self.mullan_series = self.create_continous_series(self.df2)

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

    def create_continous_series(self,df):
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
cls23 = LoadRegression()

class CLIDBData(object):

    def __init__(self, dirs, location, var_name):
        """

        :param dirs: Parent directory where the CLIDB files are located
        :param location: As before e.g. Auckland
        :param var_name: TMin, Tmax, or TMean
        """
        self.station_dict = {'Auckland':1962,'Masterton': 21938, 'Wellington':25354,
                        'Nelson':4241,'Hokitika':3909,'Lincoln':17603,'Dunedin':15752 }

        self.correction_factor = {'Auckland':0.00,'Masterton': -0.28, 'Wellington':-0.06,
                        'Nelson':0.00,'Hokitika':0.00,'Lincoln':0.00,'Dunedin':0.00 }


        self.location = location
        self.var_name = var_name
        self.dirs = dirs
        self.load_dset()


    def load_dset(self):

        filename = f"{self.dirs}/Monthly_7_Station_Series-{self.station_dict[self.location]}.xlsx"
        self.df = pd.read_excel(filename, index_col ='OBS_DATE')

        if self.var_name == 'TMean':
            self.df = self.df[self.df['FREQUENCY'] == 'D']
            self.df = (self.df['MIN_TEMP'] + self.df['MAX_TEMP'])/2.0
            self.df = self.df.apply(lambda a: np.around(a, 1))

            # Apply rounding to values

            self.df = self.df.dropna().resample('1MS').mean().apply(lambda a: np.around(a, 1))\
                            + self.correction_factor[self.location]

        else:
            self.df = self.df[self.df['FREQUENCY']=='D'][self.var_name]
        self.clibd_series = self.df.dropna().resample('1MS').mean().apply(lambda a: np.around(a, 1))\
                            + self.correction_factor[self.location]


class RegressOutputSeries(LoadRegression, CLIDBData):

    def __init__(self, var_name = 'TMean', parent_dirs = dirs, location= 'Auckland'):
        LoadRegression.__init__(self, var_name = var_name, parent_dirs = dirs, location= location)
        CLIDBData.__init__(self, var_name=var_name, dirs=parent_dirs, location=location)

    @staticmethod
    def create_anomalies_series(a, b):
        frame = pd.DataFrame(b)
        frame['value'] = b
        frame['data'] = a

        def demean(x):
            return np.around(x - np.around(x['value'].loc["1981":"2010"].mean(),2),2)

        return frame[['data', 'value']].groupby(frame.index.month).apply(demean)

    @staticmethod
    def scale_seris(a):
        mean = np.nanmean(a)
        std = np.nanstd(a)
        return (a - mean) / std, mean, std

    def monthly_regression(self):
        a, b = self.clibd_series, self.mullan_series
        series = self.create_anomalies_series(a, b)

        series = series.dropna()
        x, y = series['data'], series['value']
        series1 = series['data']
        month_idx = series.index.month.unique()
        correlations = []
        for idx in month_idx:
            x1 = x.loc[x.index.month == idx].loc["2010":]
            y1 = y.loc[y.index.month == idx].loc["2010":]
            # Subsetting the data by month

            uni_x, mu_x, std_x = self.scale_seris(x1)
            uni_y, mu_y, std_y = self.scale_seris(y1)

            # Outputting a scale serries of observations

            x2 = uni_x * std_y + mu_y
            f = linregress(x2, y1)
            print(f.slope)
            x1 = x2.apply(lambda a: f.slope*a + f.intercept)
            x.loc[x.index.month == idx] = x1

            correlations.append([f.slope, f.intercept, f.rvalue])
        series2 = pd.DataFrame(x)
        series2['data'] = x
        series2['value'] = y
        return series2,correlations, series1



locations = ['Auckland', 'Masterton', 'Wellington', 'Nelson','Hokitika','Lincoln', 'Dunedin']
corrs = []
in_series = []
old_series1 = []
old_series2 = []
for location in locations:

    cls = RegressOutputSeries(var_name='TMean',location = location)
    out_series, correlations, old_series = cls.monthly_regression()
    corrs.append(correlations)
    in_series.append(out_series)

    old_series1.append(old_series)
    old_series2.append(cls.mullan_series)


cls22 = LoadRegression(var_name='TMean',location = 'NZT7')
df22 = pd.DataFrame()
df23 = pd.DataFrame()
for i in range(7):
    df22[i] = old_series1[i].apply(lambda a: np.around(a, 2))
    df23[i] = in_series[i]['value']#old_series1[i]#'data']
export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}

import matplotlib.pyplot as plt
station_series = pd.DataFrame(df22.T.mean().apply(lambda a: np.around(a, 2)))
station_series['Nellys'] =df23.T.mean().apply(lambda a: np.around(a, 2))
station_series['Mullan'] = cls22.mullan_anomalies
fig, ax =plt.subplots()
station_series.loc["2018":].plot(ax = ax)
# df1 = pd.DataFrame(station_series, columns=['Updated Series'])
# df1['Mullan Series'] =cls22.mullan_anomalies
# df1.loc["2010":].plot(ax = ax)
fig.show()

cls.mullan_series.loc["2015":].corr(cls.clibd_series)

import tensorflow.keras as keras
input = keras.layers.Input((7,))

bn = keras.layers.BatchNormalization()(input)
bn1 = keras.layers.Dense(3, activation = 'linear')(bn)
bn1 = keras.layers.BatchNormalization()(bn1)
output = keras.layers.Dense(1, activation = 'linear')(bn1)
model = keras.models.Model(input, output)
model.compile(loss ='mse', optimizer ='adam', metrics =['mse','mae'])
from sklearn.model_selection import train_test_split
idx = cls22.mullan_anomalies.index.intersection(df22.dropna().index)
x_train,x_test,y_train,y_test = train_test_split(df22.dropna().loc[idx],
                                                 cls22.mullan_anomalies.loc[idx], shuffle=False,
                                                 test_size=0.15)
model.fit(x_train, y_train, validation_data =(x_test,y_test), epochs =202)

preds = model.predict(x_test).ravel()
y_test1 = pd.DataFrame(y_test)
y_test1['prediction'] = preds
y_test1['Original'] = station_series['Nellys'].loc[y_test.index]
fig, ax =plt.subplots(figsize =(20,12))
y_test1.loc["2000":].plot(ax = ax)
fig.show()
fig.savefig('Seven_Station_Series_test.pdf', dpi =300)

np.nanmean(abs(df1['Mullan Series'].loc["2010":] - df1['Updated Series'].loc["2010":])**2)


cls = LoadRegression(var_name='TMean',location = 'NZT7')



cls2 = CLIDBData(dirs, location='Auckland',var_name='TMean')
data = cls2.load_dset()

# hAVE subtracted the 2010 -1981 mean and it works out

from scipy.stats import linregress

out_series , series, correlations = cls.monthly_regression()#cls2.series, cls.series)

fig, ax =plt.subplots()
out_series.loc["2015":].plot(ax =ax)
fig.show()

np.nanmean(abs(out_series.loc["2015":]))





series = create_anomalies_series(cls2.series, cls.series)

data = cls.series.loc["1981":"2010"]
#


directory = r"C:\Users\rampaln\OneDrive - NIWA\Research Projects\Temperature Anomalies\Copy of NZT7_Adjusted_TMean_Anomalies2020_updated.xlsx"
df2 = pd.read_excel(directory)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
       'Oct', 'Nov', 'Dec']
df2[months] = df2[months].iloc[:-1] +df2[months].iloc[-1]
convert = pd.melt(df2, id_vars=["Year"])




import matplotlib.pyplot as plt

#convert['value'].plot()
fig, ax = plt.subplots()
convert['nellys_processing'] = df[0]
convert[['nellys_processing','value']].loc["2015":].plot(ax=ax)
fig.show()
loc = convert.dropna().index
fig = plt.figure()
plt.plot(convert['nellys_processing'].loc[loc].values, convert['value'].loc[loc].values, 'rx', label = '$r^2$ =0.99')
plt.xlabel('Nellys Series')
plt.ylabel('7 Station Series')
plt.legend()
fig.savefig('')
fig.show()
print(np.nanmean(abs(convert['nellys_processing'].loc[loc].values- convert['value'].loc[loc].values)))
from scipy.stats import linregress
f = linregress(convert['nellys_processing'].loc[loc].values,convert['value'].loc[loc].values)
convert['corrected'] = convert['nellys_processing'].apply(lambda a: a*f.slope +f.intercept)
print(np.nanmean(abs(convert['corrected'].loc[loc].values- convert['value'].loc[loc].values)**2))
def demean(x):
    return x - x['value'].mean()

corrected = convert[['nellys_processing','value']].groupby(convert.index.month).apply(demean)
loc = corrected.dropna().index
f = linregress(corrected['nellys_processing'].loc[loc].values,corrected['value'].loc[loc].values)
corrected['corrected'] = corrected['nellys_processing'].apply(lambda a: a*f.slope +f.intercept)
fig, ax =plt.subplots()
corrected[['corrected','value']].loc["2015":].plot(ax = ax)
fig.show()