import os
import shutil
import glob
files = glob.glob(r'/nesi/nobackup/niwa00004/meyerst/projects/SCO_hub/figures/*.png')
dest = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/scohub/figures'

for file in files:
    shutil.copy(file, dest)
