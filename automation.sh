#alias brc='source ~/.bashrc'
#source /home/rampaln/.bashrc
/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/run_niwa_soi.py
echo "completed script"

#HOME=/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices git commit -m "new config"

#alias git_home="HOME=/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices git"
cd /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi


/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/CEI/compute_cei.py

/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/indices/code/compute_indices.py

# Running the IOD scripts
echo "checking for new data"
/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/code/GetNOAAERSSTV5.py

/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/code/create_plots.py
echo "finished creating script"

# Running a script to calculate the IPO
/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/IPO/code/Run_IPO.py
echo "created the IPO"

/nesi/project/niwa00004/rampaln/bin/python /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/mjo_series/run_mjo.py

git add *
git commit -a -m "Auto updated"
git push

