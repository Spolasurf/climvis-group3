"""Plenty of useful functions doing useful things."""
import os
from tempfile import mkdtemp
import shutil
import xarray as xr
import numpy as np
from motionless import DecoratedMap, LatLonMarker
from climvis import cfg, graphics

GOOGLE_API_KEY = 'AIzaSyAjPH6t6Y2OnPDNHesGFvTaVzaaFWj_WCE'


def haversine(lon1, lat1, lon2, lat2):
    """Great circle distance between two (or more) points on Earth

    Parameters
    ----------
    lon1 : float
       scalar or array of point(s) longitude
    lat1 : float
       scalar or array of point(s) longitude
    lon2 : float
       scalar or array of point(s) longitude
    lat2 : float
       scalar or array of point(s) longitude

    Returns
    -------
    the distances

    Examples:
    ---------
    >>> haversine(34, 42, 35, 42)
    82633.46475287154
    >>> haversine(34, 42, [35, 36], [42, 42])
    array([ 82633.46475287, 165264.11172113])
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return c * 6371000  # Radius of earth in meters


def get_cru_timeseries(lon, lat):
    """Read the climate time series out of the netcdf files.

    Parameters
    ----------
    lon : float
        the longitude
    lat : float
        the latitude

    Returns
    -------
    a pd.DataFrame with additional attributes: ``grid_point_elevation`` and
    ``distance_to_grid_point``.
    """

    with xr.open_dataset(cfg.cru_tmp_file) as ds:
        tmp_ts = ds.tmp.sel(lon=lon, lat=lat, method='nearest')
        df = tmp_ts.to_dataframe()
    with xr.open_dataset(cfg.cru_pre_file) as ds:
        pre_ts = ds.pre.sel(lon=lon, lat=lat, method='nearest')
        df['pre'] = pre_ts.to_series()
    with xr.open_dataset(cfg.cru_topo_file) as ds:
        z = float(ds.z.sel(lon=lon, lat=lat, method='nearest'))

    df.grid_point_elevation = z
    df.distance_to_grid_point = haversine(lon, lat,
                                          float(pre_ts.lon),
                                          float(pre_ts.lat))
    return df


def get_googlemap_url(lon, lat, zoom=10):

    dmap = DecoratedMap(lat=lat, lon=lon, zoom=zoom,
                        size_x=640, size_y=640,
                        maptype='terrain', key=GOOGLE_API_KEY)
    dmap.add_marker(LatLonMarker(lat, lon))
    return dmap.generate_url()


def mkdir(path, reset=False):
    """Checks if directory exists and if not, create one.

    Parameters
    ----------
    reset: erase the content of the directory if exists

    Returns
    -------
    the path
    """

    if reset and os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    return path


def write_html(lon, lat, directory=None, zoom=None):

    # Set defaults
    if directory is None:
        directory = mkdtemp()

    if zoom is None:
        zoom = cfg.default_zoom

    # Info string
    lonlat_str = '({:.3f}E, {:.3f}N)'.format(abs(lon), abs(lat))
    if lon < 0:
        lonlat_str = lonlat_str.replace('E', 'W')
    if lat < 0:
        lonlat_str = lonlat_str.replace('N', 'S')

    mkdir(directory)

    # Make the plot
    png = os.path.join(directory, 'annual_cycle.png')
    df = get_cru_timeseries(lon, lat)
    graphics.plot_annual_cycle(df, filepath=png)

    outpath = os.path.join(directory, 'index.html')
    with open(cfg.html_tpl, 'r') as infile:
        lines = infile.readlines()
        out = []
        url = get_googlemap_url(lon, lat, zoom=zoom)
        for txt in lines:
            txt = txt.replace('[LONLAT]', lonlat_str)
            txt = txt.replace('[IMGURL]', url)
            out.append(txt)
        with open(outpath, 'w') as outfile:
            outfile.writelines(out)

    return outpath
