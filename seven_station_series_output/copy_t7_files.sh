#!/bin/bash
/nesi/project/niwa00004/rampaln/bin/python3 "/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/seven_station_series_output/copy_seven_station_series_data.py"

cd /scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/seven_station_series_output/
git add *
git commit -m "add new images"
git push
