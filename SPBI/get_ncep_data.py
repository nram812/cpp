import wget
import json
import datetime
import os
import sys
import xarray as xr
import numpy as np

with open('./SPBI/data_config.json', 'r') as f:
    config = json.load(f)
# make the directories
if not os.path.exists(f'{config["ncep"]["output_path"]}'):
    os.makedirs(f'{config["ncep"]["output_path"]}')

if not os.path.exists(f'{config["ncep"]["output_ncep_subdaily_data"]}'):
    os.makedirs(f'{config["ncep"][ "output_ncep_subdaily_data"]}')


def identify_missing_files(output_path, download_loc):
    """

    :param output_path: path where ncep data is to be stored
    :return:
    """
    current_year = datetime.datetime.utcnow().year
    ncep_years = np.arange(1948, current_year+1)
    files_names = [f'{download_loc}hgt.{year}.nc'
           for year in ncep_years if not os.path.exists(f'{output_path}/hgt.{year}.nc')]
    # identifies any other missing files if any
    files_names.append(f'{download_loc}hgt.{current_year}.nc')
    # removing the most recent one to avoid over writing
    try:
        os.remove(f'{output_path}/hgt.{current_year}.nc')
    except FileNotFoundError:
        pass
    # adds the most recent file just incase it is missing
    return list(np.unique(files_names))


files = identify_missing_files(config["ncep"]["output_path"],
                               config['ncep']['ncep_data'])
files_subdaily = identify_missing_files(config["ncep"]["output_ncep_subdaily_data"],
                                        config["ncep"]['ncep_subdaily_data'])
for file in files:
    wget.download(file, config["ncep"]["output_path"])
for file in files_subdaily:
    wget.download(file, config["ncep"]["output_ncep_subdaily_data"])
# loading the config file
