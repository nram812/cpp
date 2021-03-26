import xarray as xr

import matplotlib.pyplot as plt
import sys
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import xarray as xr
import os
import numpy as np
import glob
from joblib import dump, load
from sklearn.cluster import KMeans
len(glob.glob("/scale_wlg_nobackup/filesets/nobackup/niwa00004/rampaln/GEFS_forecast/data/20201208/*"))
from scipy.stats import linregress
sys.path.append('/scale_wlg_nobackup/filesets/nobackup/niwa00004/rampaln/GEFS_forecast/data/synoptic_types_data/')
import class_for_Kidson_types_updated as funcs
output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/solver_data'

dirs = '/scale_wlg_nobackup/filesets/nobackup/niwa00004/rampaln/GEFS_forecast/data/synoptic_types_data/NCEP_total_dset.nc'
ncep_path = r'/scale_wlg_nobackup/filesets/nobackup/niwa00004/rampaln/GEFS_forecast/data/synoptic_types_data/6-hourly'
import xarray as xr
#df = xr.open_dataset(r"C:\Users\rampaln\OneDrive - NIWA\Research Projects\CAOA2101\New_Synoptic_Types\data\NCEP_NCAR\daily\hgt.1972.nc")
# import correctlu
#
ncep_anomalies  =funcs.KidsonTypeProcessing(ncep_path, dtype = 'ncep',
                                        start_date = "1950-1-1",
                                        end_date = "2000-01-01", anom= False,)
pc_components, solver, scaler = funcs.KidsonTypeProcessing.fit_eofs(ncep_anomalies,explained_variance = 0.90)


dump(solver, f'{output_dirs}/pca_solver.joblib')
dump(scaler, f'{output_dirs}/scaler.joblib')

import pickle

kmeans = KMeans(n_clusters = 12)
kmeans.fit(pc_components)
centroids = kmeans.cluster_centers_
labels = kmeans.labels_
for i in range(12):
    print(len(labels[labels == i])/ len(labels), f'Cluster :{i+1}')
dump(kmeans, f'{output_dirs}/kmeans.joblib')
def plot_centroids(centroids, dset, subplots=(2, 4)):
    print("Plotting Centriods ........")
    n_plots = len(centroids)
    if len(subplots)>1:
        fig, ax = plt.subplots(subplots[0], subplots[1], figsize=(12, 8),
                           subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)))
    else:
        fig, ax = plt.subplots(subplots, figsize=(12, 8),
                           subplot_kw=dict(projection=ccrs.PlateCarree(central_longitude=171.77)))
    ax = ax.ravel()
    for i in range(n_plots):
        float2 = len(labels[labels == i])/ len(labels) *100
        ax[i].set_title(f'{mapping[i]} - {"%.0f" % float2}%', fontsize = 12)
        cs2 = funcs.make_map(centroids[i],
                       dset.lons_grid,
                       dset.lats_grid,
                       ax=ax[i])

    return fig
mapping = {0: "Cluster 1: HE",
           1: "Cluster 2: Ridge",
           2: "Cluster 3: T",
           3: "Cluster 4: Westerly",
           4: "Cluster 5: HNW",
           5: '',
           6: 'Cluster 7: SW',
           7:'',
           8:'',
           9:'',
           10:'Cluster 11: TNW',
           11:'Cluster 12: TSW'
           }

centre = solver.inverse_transform(centroids)
centre = scaler.inverse_transform(centre).reshape((12,13,11))
fig = plot_centroids(centre, ncep_anomalies, subplots=(3,4))
fig.tight_layout()
fig.show()
fig.savefig('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/figures/Cluster-Centroids.png')

