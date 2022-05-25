#Daily feed of observations data going into the github repository this 
# will run daily
cd /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices

echo "computing the mjo"
/nesi/project/niwa00004/rampaln/bin/python3 "/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/mjo_series/get_mjo_data.py"
echo "running plotting script"
/nesi/project/niwa00004/rampaln/bin/python "/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/mjo_series/run_mjo.py"

#running the realtime soi
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/code/compute_indices.py"
/nesi/project/niwa00004/rampaln/bin/python "/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/ross_sea_WR/run_ross_sea.py"
echo | git status
#git add *
#git commit -a -m "Auto updated"
#git push
git add ./mjo_series/*
git add ./indices/figures/*
git add ./ross_sea_WR/data/*
git commit -a -m "auto commit"
git push origin main


echo "logged" > log.log

