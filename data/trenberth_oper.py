import xarray as xr
from dask.diagnostics import ProgressBar
import matplotlib.pyplot as plt
import pandas as pd
# M1 = HOBA - CHAT
import numpy as np
# INDEX: Z1 = AUCK - CHCH
hobart_coords = (-42.880554, 147.324997)
auckland_coords = (-36.850109, 174.767700) #albert park
chatham_coords = ( -43.8923, 176.5240)
chch_coords = (-43.525650,172.639847)

df = xr.open_dataset(r"/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/era5_single_level_observations.nc", chunks={"time":10})
df = df.mean("expver")
with ProgressBar():
    df2 = xr.open_dataset(r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/monthly_single_levels_historical.nc', chunks={"time":10})
    merged_df = xr.merge([df, df2])
with ProgressBar():
    merged_df.to_netcdf(r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/monthly_single_levels_era5_complete.nc')
with ProgressBar():
    df_updated = merged_df.groupby(merged_df.time.dt.month).apply(lambda a: a - a.sel(time = slice("1961", "1990")).mean("time"))#.compute()
#df = df.mean("expver")
m1 = df_updated['msl'].interp(latitude =hobart_coords[0], longitude = hobart_coords[1], method='linear') - \
     df_updated['msl'].interp(latitude =chatham_coords[0], longitude = chatham_coords[1], method='linear')
#m1 = m1.mean
# ("expver")

z1 = df_updated['msl'].interp(latitude =auckland_coords[0], longitude = auckland_coords[1], method='linear') - \
     df_updated['msl'].interp(latitude =chch_coords[0], longitude = chch_coords[1], method='linear')
#z1 = z1.mean("expver")
with ProgressBar():
    m11 = m1.compute().to_dataframe()//10.0
    z11 = z1.compute().to_dataframe()//10.0
ddf = pd.read_csv(r"/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/data/monthly.csv",
                  parse_dates=True, index_col =0)
print(ddf['m1_0'].corr(m11['msl']),
ddf['z1_0'].corr(z11['msl'])
)
from scipy.stats import linregress
common = ddf.index.intersection(m11.loc[:].index)
# notes linear slope appears to be consistent in time
f = linregress( z11.loc[common]['msl'],ddf['z1_0'].loc[common])
# adjustment
z11['msl'] = z11['msl'].apply(lambda a: a*f.slope + f.intercept)

f2 = linregress( m11.loc[common]['msl'],ddf['m1_0'].loc[common])
# adjustment
m11['msl'] = m11['msl'].apply(lambda a: a*f2.slope + f2.intercept)
m11['Original'] = ddf['m1_0']
z11['Original'] = ddf['z1_0']
fig, ax = plt.subplots(2)
ax[0].set_title("Z1 Index Comparison")
z11.loc["1980":"2010"].plot( ax = ax[0])
m11.loc["1980":"2010"].plot( ax = ax[1])
ax[1].set_title("M1 Index Comparison")
fig.show()

#m11['msl'] = np.int(m11['msl'])/10.0


fig, ax = plt.subplots()
df['msl'].isel(time =-12, expver =0).plot(ax = ax)
fig.show()