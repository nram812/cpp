#Daily feed of observations data going into the github repository this 
# will run twice monthly
cd /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices
echo "getting data"
/nesi/project/niwa00004/rampaln/bin/python3 "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/code/GetNOAAERSSTV5.py"
echo "downloaded data"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/code/update_create_plots.py"
echo "created iod_plot"
#running the realtime soi
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/code/compute_indices.py"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/CEI/compute_cei.py"
echo "creating ipi plots"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IPO/code/Run_IPO.py"
echo "creating sio plots"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/run_niwa_soi.py"
echo "computing the sam"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/SAM/sam.py"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/SAM/sam_eof.py"
echo "getting trenberth data"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/get_single_levels_reanal.py"
echo "creating trenberth plots"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/trenberth_compute.py"

# adding gitub stuff
git add ./trenberth_figures/*
git add ./seven_station_series_output/*
git add ./niwa_soi/*
git add ./mjo_series/*
git add ./IPO/*
git add ./IOD/figures/*
git add ./CEI/*
git commit -a -m "added new plots"
git push origin main
