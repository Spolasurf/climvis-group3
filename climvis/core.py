"""Plenty of useful functions doing useful things."""
import os
#import sys # added for sys.exit in write html for locations over sea
from tempfile import mkdtemp
import shutil
import xarray as xr
import numpy as np
import pandas as pd
from motionless import DecoratedMap, LatLonMarker
from climvis import cfg, graphics
import xml.sax
import csv

from climvis.Skitour import Data_Handler, Skitour
from climvis.gpx_reader import Gpx_point

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
    #print(df.distance_to_grid_point) # i think this is in meters
    return df


class GPXHandler(xml.sax.handler.ContentHandler):
    """
    a class that defines a new parser specific for .gpx files
    in order for xml.sax to work with .gpx files
    taken from https://github.com/ryancox/motionless/blob/master/examples/munich.py


     Attributes
    ------------
    gmap: DecoratedMap (from motionless)
        has attribute self.gmap.path, a list containing str(lat, lon) elements


    first: bool
        default value "True", needed to set starting Marker on gmap, then set to "False"

    prev: tuple
        contains two values, lat and lon values as string elements


    Methods
    ------------
    startElement(name, attrs)
        function that appends the lat and lon coordinates of the trackpoints "trkpt" in the .gps file to the list self.gmap.path
        (add_path_latlon is a method of the class DecoratedMap)
        self.gmap.path is then list of string elements ['lat1,lon1', 'lat2, lon2', ...]

        it also sets self.prev elements to be the lat and lon values last read by the if loop

        lastly, it produces a marker on gmap for the first trackpoint

    enElement()
        takes the last trackpoint in .gpx and makes a marker on gmap for it
    """

    def __init__(self, gmap):
        """
        Property
        ------------
        gmap: DecoratedMap (from motionless)
            has attribute self.gmap.path, a list containing str(lat, lon) elements

        first: bool
            default value "True", needed to set starting Marker on gmap, then set to "False"

        prev: tuple
            contains two values, lat and lon values as string elements

        """

        self.gmap = gmap
        self.first = True
        self.prev = None

    def startElement(self, name, attrs):

        """
        function that appends the lat and lon coordinates of the trackpoints "trkpt" in the .gps file to the list self.gmap.path
        (add_path_latlon is a method of the class DecoratedMap)
        self.gmap.path is then list of string elements ['lat1,lon1', 'lat2, lon2', ...]

        it also sets self.prev elements to be the lat and lon values last read by the if loop

        lastly, it produces a marker on gmap for the first trackpoint

        Parameters
        ----------
        name : string
            per default, in .gpx files trakpoints are indicated with 'trkpt', this allows the parser to recognize them
        attrs : xml.sax.xmlreader.AttributesImpl
            dictionary like object representing per default in xml.sax startElement() call attributes
            must be instantiated by readers, substantially contains a mappinf from attribute names (eg. 'lat') to their values

        Returns
        -------
        None.

        """

        if name == 'trkpt':
            self.gmap.add_path_latlon(attrs['lat'], attrs['lon'])
            self.prev = (attrs['lat'], attrs['lon'])

            if self.first:
                self.first = False
                marker = LatLonMarker(attrs['lat'], attrs['lon'],
                                      color='green', label='S')
                self.gmap.add_marker(marker)

    def endElement(self, name):
        """
        function that creates the end marker for the last point in the .gps track

        Parameters
        ----------
        name : string
            per default, in .gpx files the track finishes with 'trk', this allows the parser to recognize the end of the track

        Returns
        -------
        None.

        """
        if name == 'trk':
            marker = LatLonMarker(self.prev[0], self.prev[1],
                                  color='red', label='E')
            self.gmap.add_marker(marker)



def get_googlemap_url(lon, lat, zoom=10):

    dmap = DecoratedMap(lat=lat, lon=lon, zoom=zoom,
                        size_x=640, size_y=640,
                        maptype='terrain', key=GOOGLE_API_KEY)
    dmap.add_marker(LatLonMarker(lat, lon))
    return dmap.generate_url()


def get_googlemap_track_url(gpx_file_path, lat_centre, lon_centre, zoom=10):
    """
    fuction that generates the url to plot the user .gpx tour on a map

    Parameters
    -------------
    gpx_file_path: string
        is the file path to the .gpx file

    lat_centre: float
        the latitude of the centre of the displayed map

    lon_centre: float
        the longitude of the  centre of the displayed map

    zoom: int, optional
        default value = 10, sets the enlargement of the map

    """

    # gets the map around the spacified coordinates and sets default size and type
    dmap = DecoratedMap(lat=lat_centre, lon=lon_centre, zoom=zoom,
                        size_x=640, size_y=640,
                        maptype='terrain', key=GOOGLE_API_KEY)

    # create xml.sax parser object named 'parser' and set GPXHandler()
    # previously defined as its'default contenthandler
    parser = xml.sax.make_parser()
    parser.setContentHandler(GPXHandler(dmap))

    # go to user input .gpx file and read it
    with open(gpx_file_path) as f:
        parser.feed(f.read())

    # generate url for dmap, default method from motionless
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

    #print(df)
    #print(df.grid_point_elevation)
    #print(np.isnan(df.grid_point_elevation))
    #print(np.min(df.lat))
    #print(np.max(df.lat))

    if np.isnan(df.grid_point_elevation) == True:
        raise Exception("Choose location over land and also not over the Antarctic!")



    #print(df.grid_point_elevation)
    #print(np.isnan(df).all())
    #print(np.isnan(np.sum(all(np.isnan(df).all()))))
    #print(np.isnan(np.sum(np.isnan(df).all())))
    #print(all(np.isnan(df)))
    #print(all(np.isnan(df).all()))
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


def write_point_html(point, directory=None, zoom=None): # lon,lat

    if isinstance(point, tuple):
        lon = point[0]
        lat = point[1]
    else:
        try:
            print('Searching for matching name...')
            path = cfg.world_cities
            data = pd.read_csv(path, sep="\t", header=None, dtype=str, encoding='utf-8')
            town_names = data.iloc[:,2]
            index = data.index[town_names == point].tolist()

            lat = float(data.iloc[index, 9])
            lon = float(data.iloc[index, 10])
        except TypeError:
            raise Exception("Couldn't find matching name in {}.".format(cfg.world_cities))

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

    snowpoint = Skitour(Data_Handler())
    snowpoint.output_folder = directory
    coordinates = Gpx_point(lat, lon)
    snowpoint.calc_snow_data_for_point(coordinates)
    snowpoint.plot_snowheight_for_dataset(snowpoint.snow_data[0])  # line 502 in Skitour

    outpath = os.path.join(directory, 'index.html')
    with open(cfg.html_tpl_point, 'r') as infile:
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




def write_track_html(gpx_file_path, lat_mean, lon_mean, gpx_name='your tour', mesg='no info yet', directory=None,
                    zoom=None):
    """


    Parameters
    ----------
    gpx_file_path : string
        is the file path to the .gpx file
    lat_mean : float
        the latitude of the starting point of the tour
    lon_mean : float
        the longitude of the starting point of the tour
    gpx_name: string
        name of the tour that is being diplayed. Default = 'your tour'.
    mesg: string
        tour info should come from Snowheight class calculations
    directory : string, optional
        directory where the html path is to be put in. The default is None.
    zoom : int, optional
        Enlargement for the map. The default is None.

    Returns
    -------
    outpath : string
        the html string for the climvis visualization with -track.

    """

    # Set defaults
    if directory is None:
        directory = mkdtemp()

    if zoom is None:
        zoom = cfg.default_zoom_track

    # Info string
    lonlat_str = '({:.3f}E, {:.3f}N)'.format(abs(lon_mean), abs(lat_mean))
    if lon_mean < 0:
        lonlat_str = lonlat_str.replace('E', 'W')
    if lat_mean < 0:
        lonlat_str = lonlat_str.replace('N', 'S')

    # outpath is the end path that genrates the html webpage
    outpath = os.path.join(directory, 'index.html')
    # open the html template for track, fill it
    with open(cfg.html_tpl_track, 'r') as infile:
        lines = infile.readlines()
        out = []
        url = get_googlemap_track_url(gpx_file_path, lat_mean, lon_mean, zoom=zoom)
        for txt in lines:
            txt = txt.replace('[GPXNAME]', gpx_name)
            txt = txt.replace('[LONLAT]', lonlat_str)
            txt = txt.replace('[IMGURL]', url)
            txt = txt.replace('[MSG]', mesg)
            out.append(txt)
        with open(outpath, 'w') as outfile:
            outfile.writelines(out)

    return outpath
