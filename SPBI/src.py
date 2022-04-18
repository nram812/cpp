import operator
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import xarray as xr
from numpy import deg2rad, sin, cos, meshgrid, gradient
from scipy import signal
import scipy.ndimage as ndimage
from shapely.geometry import Polygon
import geopandas as gpd
from cartopy.util import add_cyclic_point
import matplotlib.path as mpath
import matplotlib.pyplot as plt

def preprocess(dset, level, domain):
    dset = dset.sortby('lat')

    dset = dset.sel(level=level, lon=slice(*domain[:2]), lat=slice(*domain[2:]))
    if 'time_bnds' in dset.variables:
        dset = dset.drop('time_bnds')
    return dset

def add_cyclic_point(dset, varid='hgt', lat_name='lat', lon_name='lon', time_name='time'):
    data = dset[varid]

    lon = dset.coords[lon_name]
    lon_idx = data.dims.index(lon_name)

    wrap_data, wrap_lon = add_cyclic_point(data.values, coord=lon, axis=lon_idx)

    dset_wrap = {}
    dset_wrap[time_name] = dset[time_name]
    dset_wrap[lon_name] = ((lon_name), wrap_lon)
    dset_wrap[lat_name] = dset[lat_name]
    dset_wrap[varid] = ((time_name, lat_name, lon_name), wrap_data)

    dset_wrap = xr.Dataset(dset_wrap)

    dset = dset_wrap

    dset_wrap.close()

    del (dset_wrap)

    return dset


def make_boundary_circle(ax):
    import matplotlib.path as mpath

    theta = np.linspace(0, 2 * np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)

    ax.set_boundary(circle, transform=ax.transAxes)


def detrend_dim(da, dim, deg=1, add_average=True):
    # detrend along a single dimension
    p = da.polyfit(dim=dim, deg=deg)

    fit = xr.polyval(da[dim], p.polyfit_coefficients)

    # return the detrended + average

    if add_average:

        return (da - fit) + da.mean(dim=dim)

    else:

        return (da - fit)


def harmo(data, nbharm=2):
    """
    returns the 1st 2 harmonics calculated over a time-series
    (can be numpy.ndarray, pandas Series or Dataframe)
    """

    if isinstance(data, pd.core.frame.Series) or isinstance(data, pd.core.frame.DataFrame):

        index = data.index
        data_values = data.values.flatten()

    elif isinstance(data, np.ndarray):

        data_values = data

    fft = np.fft.rfft(data_values)
    fft[nbharm + 1] = 0.5 * fft[nbharm + 1]
    fft[nbharm + 2:] = 0

    data_f = np.fft.irfft(fft)

    if isinstance(data, pd.core.frame.Series):
        data_f = pd.Series(data_f, index=index)

    if isinstance(data, pd.core.frame.DataFrame):
        data_f = pd.DataFrame(data_f, index=index, columns=['Fourier_{}harms'.format(nbharm)])

    return data_f


def low_pass_filter(x, high=30):
    N = 2.

    B, A = signal.butter(N, N / high, btype='lowpass', output='ba')

    if any(np.isnan(x)):

        z = x

    else:

        z = signal.filtfilt(B, A, x)

    return z


def earth_radius(lat):
    """
    return the earth radius for a given latitude
    Parameters
    ----------
    lat : float
        The latitude
    Returns
    -------
    Float
        The Earth radius
    """

    lat = deg2rad(lat)
    a = 6378137
    b = 6356752
    r = (
                ((a ** 2 * cos(lat)) ** 2 + (b ** 2 * sin(lat)) ** 2)
                / ((a * cos(lat)) ** 2 + (b * sin(lat)) ** 2)
        ) ** 0.5

    return r


def area_grid(lat, lon, return_dataarray=False):
    """Calculate the area of each grid cell for a user-provided
    grid cell resolution. Area is in square meters, but resolution
    is given in decimal degrees.
    Based on the function in
    https://github.com/chadagreene/CDT/blob/master/cdt/cdtarea.m
    """
    from numpy import meshgrid, deg2rad, gradient, cos

    ylat, xlon = meshgrid(lat, lon)
    R = earth_radius(ylat)

    dlat = deg2rad(gradient(ylat, axis=1))
    dlon = deg2rad(gradient(xlon, axis=0))

    dy = dlat * R
    dx = dlon * R * cos(deg2rad(ylat))

    area = dy * dx

    if not return_dataarray:
        return area
    else:
        from xarray import DataArray

        xda = DataArray(
            area.T,
            dims=["lat", "lon"],
            coords={"lat": lat, "lon": lon},
            attrs={
                "long_name": "area_per_pixel",
                "description": "area per pixel",
                "units": "m^2",
            },
        )
        return xda


def recode(dataarray, threshold=1, comparison='>=', mask=None):
    """
    [summary]

    [extended_summary]

    Parameters
    ----------
    dataarray : [type]
        [description]
    threshold : float, int or dataarray
        [description], by default 1
    comparison : str, optional
        [description], by default '>'

    Returns
    -------
    [type]
        [description]
    """

    import numpy as np
    import operator
    import xarray as xr

    dops = {}
    dops['>'] = operator.gt
    dops['>='] = operator.ge
    dops['<'] = operator.lt
    dops['<='] = operator.le
    dops['=='] = operator.eq

    dataarray = dops[comparison](dataarray, threshold).astype('int')

    if mask is not None:
        dataarray = dataarray * mask

    return dataarray


def filter_sequences(x, comparison='>=', min_duration=5):
    """
    filter sequences, in a series of boolean values (0 or 1)
    lasting more or less than (or exactly equal to) `min_duration`
    """

    dops = {}
    dops['>'] = operator.gt
    dops['>='] = operator.ge
    dops['<'] = operator.lt
    dops['<='] = operator.le
    dops['=='] = operator.eq

    if np.sum(x) == np.nan:

        x_recode = x

    else:

        x_recode = np.zeros_like(x)

        events, n_events = ndimage.label(x)

        # Find all events of duration >= minDuration

        start_index = []
        end_index = []
        duration = []

        for ev in range(1, n_events + 1):

            event_duration = (events == ev).sum()

            if dops[comparison](event_duration, min_duration):
                istart = np.where(events == ev)[0][0]
                iend = np.where(events == ev)[0][-1]

                start_index.append(istart)
                end_index.append(iend)
                duration.append(iend - istart + 1)

                x_recode[istart:iend + 1] = 1

    return np.array(start_index), np.array(end_index), np.array(duration), x_recode


def extract_sequences(pc, threshold=1, comparison='>=', min_duration=5):
    pc = recode(pc, threshold=threshold, comparison=comparison)

    istart, iend, duration, x_recode = filter_sequences(pc, min_duration=min_duration)

    pc_recode = pc.copy()

    index = pc_recode.to_pandas().index[istart]

    dates_start = index

    dates_end = []

    for i, d in enumerate(dates_start):
        dates_end.append(d + timedelta(days=int(duration[i] - 1)))

    dates_end = np.array(dates_end)

    return pd.DataFrame(index=index, data={'time': istart, 'event_duration': duration, 'event_start': dates_start,
                                           'event_end': dates_end})


def gpd_from_domain(lonmin=None, lonmax=None, latmin=None, latmax=None, crs='4326'):
    """
    creates a geopandas dataframe with a rectangular domain geometry from
    min and max longitudes and latitudes

    can be called using gpd_from_domain(*[lonmin, lonmax, latmin, latmax])

    can be passed e.g. to get_one_GCM() or get_GCMs() as a `mask` keyword argument

    Parameters
    ----------
    lonmin : float, optional
        min longitude, by default None
    lonmax : float, optional
        max longitude, by default None
    latmin : float, optional
        min latitude, by default None
    latmax : float, optional
        max latitude, by default None
    crs : str, optional
        The coordinate reference system, by default '4326'

    Returns
    -------
    [type]
        [description]
    """

    # make the box

    shape = Polygon(((lonmin, latmin), (lonmax, latmin), (lonmax, latmax), (lonmin, latmax), (lonmin, latmin)))

    shape_gpd = gpd.GeoDataFrame([], geometry=[shape])

    # set the CRS

    shape_gpd = shape_gpd.set_crs(f'epsg:{crs}')

    return shape_gpd