import os
import wget
import datetime
import json
with open('./config.json', 'r') as f:
    config = json.load(f)
output_dirs = config["output_daily_ncep_directory"]
var_name = "hgt"
dirs = lambda var_name, year: f"https:" \
                              f"//downloads.psl.noaa.gov/" \
                              f"Datasets/ncep.reanalysis.dailyavgs/" \
                              f"pressure/{var_name}.{year}.nc"
cur_year = datetime.datetime.now().year
if os.path.exists(f"{output_dirs}/{var_name}.{cur_year}.nc"):
    os.remove(f"{output_dirs}/{var_name}.{cur_year}.nc")
wget.download(dirs(var_name, cur_year),
              f"{output_dirs}/{var_name}.{cur_year}.nc")