import wget
import json
import datetime
import os
with open('data_config.json', 'r') as f:
    config = json.load(f)
# make the directories
if not os.path.exists(f'{config["ncep"]["output_path"]}'):
    os.makedirs(f'{config["ncep"]["output_path"]}')
# loading the config file
year = datetime.datetime.utcnow().year
if os.path.exists(f'{config["ncep"]["output_path"]}/hgt.{year}.nc'):
    os.remove(f'{config["ncep"]["output_path"]}/hgt.{year}.nc')
# deleting the old file
wget.download(f'{config["ncep"]["ncep_data"]}/hgt.{year}.nc',
              config["ncep"]["output_path"])
# downloading the new file