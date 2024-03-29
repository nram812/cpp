import glob
import shutil
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/seven_station_series_output'
images = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/output_1991_2020/figures/NZT7_*_updated*',recursive = True)

csv_files = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/output_1991_2020/brick_format/*/*.xlsx')

# Extraction of xlsx files also
xlsx_files = glob.glob(r'/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/output_1991_2020/time_series_format/*.xlsx')

all_files =  csv_files + xlsx_files
images = sorted(images)
for file in images:
    fname = file.split('/')[-1]
    shutil.copy(file,f'{output_dirs}/figures/{fname}')

for csv in all_files:
    fname = csv.split('/')[-1]
    shutil.copy(csv,f'{output_dirs}/data/{fname}') 
