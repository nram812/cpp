import sys
import pathlib
import ftplib
import numpy as np
import pandas as pd
import xarray as xr
import os
level = 1000

def subset_netcdf(filename, parent_dirs, lonW, lonE, latN, latS):
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

    def download_ftp_data(self, filename,output_path,lonW, lonE, latN, latS, mode = 'update'):
        in_path = os.path.join(output_path, filename)
        if mode == 'update':
            try:
                os.remove(in_path)
            except FileNotFoundError:
                pass
            self.download_link(filename, in_path, output_path, lonW, lonE, latN, latS)
        else:
            self.download_link(filename, in_path, output_path, lonW, lonE, latN, latS)
        # if download mode, we download everything (the whole dataset)
    def download_link(self, filename, in_path, output_path, lonW, lonE, latN, latS):
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
                subset_netcdf(filename, output_path, lonW, lonE, latN, latS)



                if os.path.exists(in_path):
                    print(f"successfully extracted domain for {in_path}")

def subset_filenames(filenames, start_date =2020):
    df = pd.DataFrame(index = pd.to_datetime(filenames, format = "hgt.%Y.nc").year,
                      data = filenames, columns = ['fnames'])
    return df.loc[start_date:].values
