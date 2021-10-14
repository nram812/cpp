import numpy as np
import sys
import pandas as pd
import datetime as dt
import os
import pytz
import datetime
from calendar import monthrange
sys.path.append(r'/home/rampaln/python_clidb')
input_lib_dirs = r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python'

os.chdir(input_lib_dirs)
sys.path.append('lib/')
from src import *
from lib.CLIDB.ConstructQuery_new import ConstructQuery


output_dirs = f'{input_lib_dirs}/output'
mullan_old_series = './Mullan_Validation_Series'
make_output_directories(output_dirs)
# Creating a separate folder for the data

# Initialize query
query = ConstructQuery(*load_credentials())
fields = ['MTHLY_STATS']
stat_code = "02"
station_dict = {1962: 'Auckland',
                21938: 'Masterton',
                25354: 'Wellington',
                4241: 'Nelson',
                3909: 'Hokitika',
                17603: 'Lincoln',
                15752: 'Dunedin'}

correction_factor = {'Auckland': 0.00,
                     'Masterton': -0.28,
                     'Wellington': -0.06,
                     'Nelson': 0.00,
                     'Hokitika': 0.00,
                     'Lincoln': 0.00,
                     'Dunedin': 0.00}
# Extracting the current date and time for the analysis
start_date, end_date, current_year, current_month, current_date = determine_date()

corrected_data = pd.DataFrame()
anomalies = pd.DataFrame()
uncorrected_data = pd.DataFrame()
total_series = pd.DataFrame()


for station in station_dict.keys():
    data = query.extract_query([station], start_date, end_date, fields)

    corrected_anomalies, uncorrected_obs, corrected_data_series, series = create_series(data, station,
                                                                                        correction_factor, stat_code,
                                                                                        mullan_old_series, station_dict)

    anomalies[station_dict[station]] = corrected_anomalies
    corrected_data[station_dict[station]] = corrected_data_series
    uncorrected_data[station_dict[station]] = uncorrected_obs
    total_series[station_dict[station]] = series

#print(corrected_data.index)
anomalies.to_csv(f'{output_dirs}/time_series/AllStationMonthly_Anomalies.csv')
covert_series_to_brick(anomalies,output_dirs +'/bricks', output_name = 'Anomalies')
#print(corrected_data.head())
corrected_data.to_csv(f'{output_dirs}/time_series/Corrected-Data-Series.csv')
covert_series_to_brick(corrected_data,output_dirs +'/bricks',  output_name = 'Full_')
covert_series_to_brick(total_series,output_dirs +'/bricks',  output_name = 'Full_Total_Series')
uncorrected_data.to_csv(f'{output_dirs}/time_series/UncorrectedData.csv')
covert_series_to_brick(uncorrected_data, output_dirs +'/bricks', output_name = 'Uncorrected_data')

print("The Seven Station Series has Run")
