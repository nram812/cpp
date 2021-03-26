mode = 'update'
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/data_real_time'
import sys
import pathlib
import ftplib
import numpy as np
import pandas as pd
import xarray as xr
import os
from multiprocessing import Pool
import shutil

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
start_date = 2020
download_variable = 'hgt'
# %% md

def subset_netcdf(filename, parent_dirs):
    in_path = os.path.join(parent_dirs, filename)
    dset = xr.open_dataset(in_path)
    dset = dset.sel(lon=slice(lonW, lonE), lat=slice(latN, latS), level=level)
    dset = dset.squeeze()
    # flip the latitudes to go from S to N
    dset = dset.sortby('lat')
    os.remove(in_path)
    # remove the file

    # saves the extracted domain
    dset.to_netcdf(in_path)
    dset.close()


class Load_data:
    def __init__(self, ftp):
        self.ftp = ftp

    def download_ftp_data(self, filename, mode = mode):
        in_path = os.path.join(output_path, filename)
        if mode == 'update':
            os.remove(in_path)
            self.download_link(filename, in_path)
        else:
            self.download_link(filename, in_path)
        # if download mode, we download everything (the whole dataset)
    def download_link(self, filename, in_path):
        if os.path.exists(in_path):
            print(f"{filename} already downloaded and extracted in {str(output_path)}, skipping to next file")
        else:
            with open(in_path, 'wb') as f:
                self.ftp.retrbinary('RETR ' + filename, f.write)
            if not os.path.exists(in_path):
                print(f"download failed for {filename}")
            else:
                print(f"{filename} successfully downloaded in {str(in_path)}, now extracting domain")
                # Subset the netcdf file
                subset_netcdf(filename, output_path)



                if os.path.exists(in_path):
                    print(f"successfully extracted domain for {in_path}")

def subset_filenames(filenames, start_date =2020):
    df = pd.DataFrame(index = pd.to_datetime(filenames, format = "hgt.%Y.nc").year,
                      data = filenames, columns = ['fnames'])
    return df.loc[start_date:].values
if __name__ == "__main__":
    with ftplib.FTP(url) as ftp:
        ftp = ftplib.FTP(url)
        ftp.login()
        ftp.cwd(folder)
        filenames = ftp.nlst()
        cls = Load_data(ftp)
        local_path = os.getcwd()
    
        filenames = [f for f in filenames if download_variable in f]
        filenames = subset_filenames(filenames, start_date)
        agents = 2
        chunksize = 1
        arr = []
        # cls.download_ftp_data(filenames[-2])
        with Pool(processes=agents) as pool:
            pool.map(cls.download_ftp_data, filenames, chunksize)
        ftp.close()







