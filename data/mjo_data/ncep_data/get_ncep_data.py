import wget
import json
import datetime
import os
with open('./config.json', 'r') as f:
    config = json.load(f)
# loading the config file
year = datetime.datetime.utcnow().year
if os.path.exists(f'{output_daily_ncep_directory}/hgt.{year}.nc'):
    os.remove(f'{output_daily_ncep_directory}/hgt.{year}.nc')
# deleting the old file
wget.download(f'{config["SPBI_metadata"]["ncep_data"]}/hgt.{year}.nc',
              config["output_daily_ncep_directory"])
# downloading the new file