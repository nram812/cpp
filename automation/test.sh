#Daily feed of observations data going into the github repository this 
# will run daily
cd /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices

echo "computing the mjo"
/home/rampaln/.conda/envs/s7s/bin/python "/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/mjo_series/get_mjo_data.py"
echo "running plotting script"
/home/rampaln/.conda/envs/s7s/bin/python "/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/mjo_series/run_mjo.py"

echo "running SPBI"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/SPBI/get_ncep_data.py"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/SPBI/create_index.py"
#running the realtime soi
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/code/compute_indices.py"
/home/rampaln/.conda/envs/s7s/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/ross_sea_WR/run_ross_sea.py"
echo | git status
#git add *
#git commit -a -m "Auto updated"
#git push
git add ./mjo_series/*
git add ./indices/figures/*
git add ./ross_sea_WR/data/*
git add ./SPBI/figures/*
git commit -a -m "auto commit"
git push origin main


echo "logged" > log.log

