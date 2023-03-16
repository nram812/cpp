#Daily feed of observations data going into the github repository this 
# will run twice monthly
cd /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices
echo "getting data"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/code/GetNOAAERSSTV5.py"
echo "downloaded data"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/code/update_create_plots.py"
echo "created iod_plot"
#running the realtime soi
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/code/compute_indices.py"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/CEI/compute_cei.py"
echo "creating ipi plots"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IPO/code/Run_IPO.py"
echo "creating sio plots"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/run_niwa_soi.py"
echo "computing the sam"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/SAM/sam.py"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/SAM/sam_eof.py"
echo "getting trenberth data"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/get_single_levels_reanal.py"
echo "creating trenberth plots"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/trenberth_compute.py"

# adding gitub stuff
git add ./trenberth_figures/*
git add ./seven_station_series_output/*
git add ./niwa_soi/*
git add ./mjo_series/*
git add ./SAM/figures/*
git add ./IPO/figures/*
git add ./IOD/figures/*
git add ./CEI/figures/*
git commit -a -m "added new plots"
git push origin main
