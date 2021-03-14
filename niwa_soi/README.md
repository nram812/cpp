# NIWA SOI Generator:

This code was adapted from @NicolasFaucherau, and has been modified to be automated on the HPC (w-nwp01.maui.niwa.co.nz). 

This repository will update monthly and the data will also be updated monthly on this folder.

## Methodology
The methodology is based on:

Troup, A.J,, 1965: The Southern Oscillation. Quarterly Journal of Royal Meteorological Society 91, 490-506.

If T and D are the monthly pressures at Tahiti and Darwin, respectively, and Tc and Dc the climatological monthly pressures, then: 
```
SOI    =   [ (T – Tc) – (D – Dc) ]  /  [ StDev (T – D)  ]
```
## Environment:

To run the code:
```
/nesi/project/niwa00004/rampaln/bin/python3 /nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi/run_soi.py
```
This will run the code automatically.


## Running the code:

The code is run through crontab via an autocommit scheme.

To configure an autocommit scheme use the following methodology:

1. Move the .config file to a folder of your choice.
2. Define a custom home variable for your git configuration (run this):
```
HOME=/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi git commit -m "new config"
```
3. define a new config:
```
alias git_custom="HOME=/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/niwa_soi git"
git_custom commit -m "new commit"
```

You can now use "git_custom" to commit now. Sometimes you have storage issues and having this located on the project drive can be beneficial. 