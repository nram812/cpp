mode = 'update'
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/data_real_time'
import sys
import ftplib
import os
sys.path.append('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/lib')
from download_ncep import *

# Create the appropriate directories
output_path = f'{output_dirs}/NCEP_NCAR/6-hourly'
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Variables for download
url = 'ftp2.psl.noaa.gov'
folder = '/Projects/Datasets/ncep.reanalysis/pressure'
latN = 15
latS = -60
lonW = 155
lonE = 235
level = 1000
start_date = 2021
download_variable = 'hgt'
# %% md


if __name__ == "__main__":
    with ftplib.FTP(url) as ftp:
        ftp = ftplib.FTP(url)
        ftp.login()
        ftp.cwd(folder)
        filenames = ftp.nlst()
        cls = Load_data(ftp)
        local_path = os.getcwd()

        filenames = [f for f in filenames if download_variable in f]
        filenames = subset_filenames(filenames, start_date).ravel()
        for file in filenames:
            cls.download_ftp_data(file, output_path,lonW, lonE, latN, latS, mode ='update')








