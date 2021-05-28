import xarray as xr

import matplotlib.pyplot as plt
import sys
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import glob
from joblib import dump, load
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

output_dirs = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/solver_data'
scaler = load(f'{output_dirs}/scaler.joblib')
solver = load(f'{output_dirs}/pca_solver.joblib')
kmeans = load(f'{output_dirs}/kmeans.joblib')


frame = xr.open_dataset('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/data_real_time/NCEP_NCAR/6-hourly/hgt.2021.nc')
shape_dset = xr.open_dataset('/nesi/nobackup/niwa00004/rampaln/GEFS_forecast/data/synoptic_types_data/NCEP_total_dset.nc')

frame = frame.interp_like(shape_dset['hgt'].isel(time =0))
def output_preds(a):
    try:
        a = a.reshape(1, np.prod(a.shape))
        a = scaler.transform(a)
        a = solver.transform(a)
        return kmeans.predict(a.astype('float32'))[0]
    except:
        return np.nan

out = xr.apply_ufunc(output_preds, frame, input_core_dims=[["lat","lon"]],
               output_core_dims=[[]],
               vectorize=True,
               dask='allowed')

both_dsets = xr.open_mfdataset('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/data_real_time/NCEP_NCAR/6-hourly/*.nc',
                               concat_dim="time")
both_dsets = both_dsets.interp_like(shape_dset['hgt'].isel(time =0))
out_both = xr.apply_ufunc(output_preds,both_dsets, input_core_dims=[["lat","lon"]],
               output_core_dims=[[]],
               vectorize=True,
               dask='allowed')
import pandas as pd
def calculate_percentage(output, n_label=12):
    z1 = output['hgt'].to_dataframe().reset_index()
    z1.index = z1['time']
    dset_output = pd.DataFrame(index = z1.time.unique())
    dset_output2 = pd.DataFrame(index=z1.time.unique())
    for i in range(n_label):
        dset_output[i] = z1['hgt'].resample('1MS').apply(lambda a: len(a[a == i]) / len(a[a>=0.0]))
        dset_output2[i] = z1['hgt'].resample('1MS').apply(lambda a: len(a[a >= 0.0]))
    return dset_output.dropna(), dset_output2.dropna()

dset_output, counts = calculate_percentage(out_both)
import seaborn as sns
test_dset = dset_output
test_dset.index = dset_output.index.strftime("%Y-%B")
fig, ax = plt.subplots()
sns.heatmap(test_dset.T, ax = ax, cmap ='Reds')
fig.show()
fig = plt.figure(constrained_layout=True,figsize =(10,7))
gs = fig.add_gridspec(6, 2)
ax = fig.add_subplot(gs[:-1, :])
ax.set_title('Sub-seasonal Clustering for New Zealand')
ax4 = fig.add_subplot(gs[-1, :])

labels = [items[1] for items in mapping.items()]#['Northern High','Westerly','Ridge','Trough','Northeasterly']
#['Trough','Ridge','Northern High','Westerly',##'Northeasterly']
bottom =0
plts = []
cm = plt.get_cmap('gist_rainbow')
NUM_COLORS = 12
colors = []
for j in dset_output.columns:
    colors.append(cm((j/3*3.0/NUM_COLORS)))
    if j ==0:
        cs = ax.bar(np.arange(len(dset_output.index)), dset_output[0], color = cm((j/3*3.0/NUM_COLORS)))
        # cs[0].set_color(cm((j//3*3.0/NUM_COLORS)))
        #colo
        plts.append(cs)
        bottom = dset_output[0].copy()
    else:
        cs = ax.bar(np.arange(len(dset_output.index)), dset_output[j],bottom = bottom, color = cm((j/3*3.0/NUM_COLORS)))
        #cs[0].set_color(cm((j//3*3.0/NUM_COLORS)))
        bottom += dset_output[j].copy()
        plts.append(cs)
    ax.set_xticks(np.arange(len(dset_output.index)))
    ax.set_xticklabels([])
    ax.set_xlim(0, len(dset_output.index))

    #ax.set_xticklabels([str(i) for i in dset_output.index.strftime('%Y-%m-%d')], rotation ='90', fontsize =10)
    ax.legend(labels, loc = 'upper center',bbox_to_anchor=(1.15, 1.0), title = 'Synoptic Type', ncol =1)
    ax.set_yticks(np.arange(0,1.2,0.2))
    ax.set_yticklabels(['%.0f'% f for f in np.arange(0,1.2,0.2) *100])
#ax.legend(handles =plts,  title='Synoptic Type', bbox_to_anchor=(1.05, 1), loc='lower center')
ax.set_title('Sub-seasonal Clustering for New Zealand')
ax.set_ylabel('Probability (%)')
#fig.show()
import matplotlib
cmap = matplotlib.colors.ListedColormap(colors)
#ax4 = fig.add_axes([0.15, -0.05,0.7, 0.1])
output_ = np.argmax(dset_output.values, -1).reshape(1, dset_output.values.shape[0])
ax4.pcolor(output_, cmap = cmap, edgecolor ='w')
ax4.set_xticks(np.arange(len(dset_output.index)))
ax4.set_yticks([])
ax4.set_yticklabels([])
ax4.set_xlim(0, len(dset_output.index))
ax4.set_xticklabels([str(i) for i in dset_output.index], rotation='90', fontsize=10)
fig.tight_layout()
fig.show()

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

NUM_COLORS = 20

cm = plt.get_cmap('gist_rainbow')
fig = plt.figure()
ax = fig.add_subplot(111)
for i in range(NUM_COLORS):
    lines = ax.plot(np.arange(10)*(i+1))
    lines[0].set_color(cm(i//3*3.0/NUM_COLORS))
    lines[0].set_linewidth(i%3 + 1)

fig.savefig('moreColors.png')
fig.show()

fig.tight_layout()
fig.show()
fig.savefig('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/kidson_synoptic_types/figures/Cluster-Centroids.png')
