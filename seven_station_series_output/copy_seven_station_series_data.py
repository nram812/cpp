import glob
import shutil
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/seven_station_series_output'
images = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series/NZT7*',recursive = True)

csv_files = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series/Total_series_*.csv')

csv_files1 = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series/SevenStationSeries_full*.csv')
csv_files2 = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series/AllStationMonthly_Anomalies_*.csv')
all_files = csv_files2 + csv_files + csv_files1
images = sorted(images)
for file in images:
    fname = file.split('/')[-1] 
    shutil.copy(file,f'{output_dirs}/figures/{fname}')
fname = 'NZT7.png'
shutil.copy(file,f'{output_dirs}/figures/{fname}')
for csv in all_files:
    fname = csv.split('/')[-1]
    shutil.copy(csv,f'{output_dirs}/data/{fname}') 
