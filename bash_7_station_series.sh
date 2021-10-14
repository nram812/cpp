#!/bin/bash

# This is the watercare script suite to run for the reports

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
export DISPLAY=:0.0
# Export the Oracle library to the Top level directory
export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}

module load OCI/12.2
# Change to the correct home directory
cd /nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python 
echo "running python script"
/nesi/project/niwa00004/rampaln/bin/python3 seven_station_series.py
/nesi/project/niwa00004/rampaln/bin/python send_series.py
/nesi/project/niwa00004/rampaln/bin/python3 /scale_wlg_persistent/filesets/project/niwa00004/rampaln/water-rainfall-repository/pressure_plots/MSLP_anomally_script.py 
cd /home/rampaln/python_clidb
/nesi/project/niwa00004/rampaln/bin/python3 vcsn_rainfall_query_for_climate_summarios_final.py

