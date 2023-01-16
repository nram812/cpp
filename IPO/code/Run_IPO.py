import sys
from matplotlib import pyplot as plt
import pathlib
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import xarray as xr
from cartopy import crs as ccrs
from cartopy import config
from scipy import signal
from eofs.standard import Eof
import os
os.chdir('/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
import os
os.chdir(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices')
sys.path.append(r'./lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *
from cei_funcs import *



years, months, mFMT, yFMT = load_plotting_config__()
config['data_dir'] ='/nesi/project/niwa00004/rampaln/cartopy'
if __name__ == "__main__":

    out_file = "./IPO/figures/All_IPO.png"
    dset = xr.open_dataset(r'./IOD/data/sst_dset.nc')
    dset = dset.sel(lat=slice(-50,50), lon=slice(120,295))
    dset = dset.sortby("time")
    def create_mask(dset):
        sst_arr = dset['sst'].data
        sst_arr = sst_arr.mean(0)
        sst_arr = sst_arr[:,50::]
        idx = np.empty((sst_arr.shape[0]))

        for i in range(sst_arr.shape[0]):
            idx[i,] = np.where(np.isnan(sst_arr[i,:]))[0].min()
        idx_shift = 50 + idx
        mask = np.ones(dset['sst'].shape[1:])


        for i in range(mask.shape[0]):
            mask[i,int(idx_shift[i])::] = np.nan

        dset['mask'] = (('lat','lon'), mask)
        dset['sst_masked'] = dset['sst'] * dset['mask']
        return dset
    dset = create_mask(dset)

    def demean(x):
        return x - x.sel(time=slice('1981','2010')).mean('time')
    sst_anoms = dset[['sst_masked']].groupby('time.month').apply(demean)


    def compute_ipo(sst_anoms, years_pass =11, N =2.0):
        high = np.int(years_pass * 12.)
        B, A = signal.butter(N, N/high, btype='lowpass', output='ba')

        def filter_SST(x):
            if any(np.isnan(x)):
                z = x
            else:
                z = signal.filtfilt(B, A, x)
            return z

        sst_anoms['sst_filtered'] = (('time', 'lat', 'lon'), np.apply_along_axis(filter_SST, 0, sst_anoms['sst_masked'].data))


        lat = sst_anoms['lat'].values
        lon = sst_anoms['lon'].values
        lons, lats = np.meshgrid(lon, lat)
        coslat = np.cos(np.deg2rad(lat))
        wgts = np.sqrt(coslat)[..., np.newaxis]
        sst_anoms.load()
        X = sst_anoms['sst_filtered'].data
        solver = Eof(X, weights=wgts)
        eofs = solver.eofsAsCorrelation(neofs=5)
        pcs = solver.pcs(npcs=5, pcscaling=1)
        PCs = pd.DataFrame(pcs, index=sst_anoms['time'].to_index())
        PCs_monthly = solver.projectField(sst_anoms['sst_masked'].data,5)
        PCs_monthly = pd.DataFrame(PCs_monthly, index=sst_anoms['time'].to_index())
        return eofs, PCs, lons, lats,PCs_monthly

    eofs, PCs, lons, lats, PCs_monthly = compute_ipo(sst_anoms, years_pass=11, N=2.0)


    n_eof = 0
    f, ax = plt.subplots(subplot_kw={'projection':ccrs.PlateCarree(central_longitude=180)})
    im = ax.contourf(lons, lats,  eofs[n_eof,:,:], transform=ccrs.PlateCarree(), levels=np.arange(-1, 1.1, 0.1), cmap=plt.cm.RdBu_r)
    cbar = f.colorbar(im,ax = ax, shrink=0.7)
    cbar.set_label(u'SST Anomalies (\N{DEGREE SIGN} C)')
    ax4 = f.add_axes([0.05,0.1,0.9,0.1])
    ax4.axis('off')
    ax.coastlines()
    create_watermark(f,
                     label=None, ax=ax, alpha=1, loc="lower right")
    f.suptitle('EOF 0')
    f.savefig("./IPO/figures/IPO_eof0.png", dpi =300)

    n_eof = 1
    f, ax = plt.subplots(subplot_kw={'projection':ccrs.PlateCarree(central_longitude=180)})
    im = ax.contourf(lons, lats,  eofs[n_eof,:,:], transform=ccrs.PlateCarree(), levels=np.arange(-1, 1.1, 0.1), cmap=plt.cm.RdBu_r)
    cbar = f.colorbar(im,ax = ax, shrink=0.7)
    cbar.set_label(u'SST Anomalies (\N{DEGREE SIGN} C)')
    ax4 = f.add_axes([0.05,0.1,0.9,0.1])
    ax4.axis('off')
    ax.coastlines()
    create_watermark(f,
                     label=None, ax=ax, alpha=1, loc="lower right")
    f.suptitle('EOF 1')
    f.savefig("./IPO/figures/IPO_eof1.png", dpi =300)

    PCs.to_csv('./IPO/data/IPO.csv')
    PCs_monthly.to_csv('./IPO/data/IPO_monthly.csv')
    PCs.to_csv('./IPO/data/IPO.xlsx')
    PCs_monthly.to_csv('./IPO/data/IPO_monthly.xlsx')
    GW = PCs.loc[:,0]
    f, ax = plt.subplots(figsize=(10,6))
    ax.fill_between(GW.index,GW.values, 0, (GW.values>=0), color='coral', alpha=.9, interpolate=True)
    ax.fill_between(GW.index,GW.values, 0, (GW.values<0), color='steelblue', alpha=.9, interpolate=True)
    ax.plot(GW.index, GW.values, c='k')
    ax.grid('on')
    ax.axhline(0,c='0.4')
    f.suptitle('PC #1 : Global Warming', fontsize=14)
    create_watermark(f,
                     label=None, ax=ax, alpha=1, loc="lower right")
    ax.set_xlabel('Year')
    ax.set_ylabel('PC # 1')
    f.tight_layout()
    f.savefig("/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/IPO/figures/global_warming.png")


    IPO = -1 *PCs.loc[:,1].iloc[-150:]
    f, ax = plt.subplots(figsize=(10,6))
    ax.fill_between(IPO.index,IPO.values, 0, (IPO.values>=0), color='coral', alpha=.9, interpolate=True)
    ax.fill_between(IPO.index,IPO.values, 0, (IPO.values<0), color='steelblue', alpha=.9, interpolate=True)
    ax.plot(IPO.index, IPO.values, c='k')
    ax.grid('on')
    ax.axhline(0,c='0.4')
    create_watermark(f,
                     label=None, ax=ax, alpha=1, loc="lower right")
    f.suptitle('PC #2 : Interdecadal Pacific Oscillation (IPO)', fontsize=14)



    f.savefig("./IPO/figures/IPO_IPO.png", dpi =300)
    dates, widths, soi, soim = format_series_for_bar_plot__(ts_soi=PCs.loc["2016":], col1 =1, col2 = 0, weekly = False)
    fig, ax, __, new_fig_created,textBm, textBs = plot_data(dates, soi, widths,
                                                      soim, months,
                                                      output_path=f"./IPO/figures/",
                                                      cei = True, var_name ='IPO', var_2 = 'SOI 3-month', ylim = (-3,3), periodicity = 'M',
                                                            period1 =1, period2 =3)
    #Mantua, Nathan J., et al. "A Pacific interdecadal climate oscillation with impacts on salmon production." Bulletin of the american Meteorological Society 78.6 (1997): 1069-1080.
    add_reference(ax, 12, [textBm, textBs], top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref="Ref: Mantua, Nathan J., et al, 1997, N; DOI: 10.1175/1520-0477(1997)078")
    ax.set_xlim(dates[0], dates[-1] + pd.Timedelta(days=30))
    ax.grid(False)
    fig.tight_layout()
    fig.show()
    fig.savefig(out_file, dpi=300)
    #handle_figure_update_mssg(out_file, True)




