# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 11:52:13 2020

@author: Laurin Steinmaier
"""

import matplotlib.pyplot as plt  # plotting library
import numpy as np  # numerical library
import xarray as xr  # netCDF library
from scipy.stats import norm
import datetime as dt
from scipy.interpolate import interp1d
from matplotlib.collections import LineCollection
from scipy.ndimage.filters import gaussian_filter1d
import os.path




class Data_Handler:
    """
    ***Not ready yet -> only test phase***
    
    A class which contains and manages data files.
    
    Relevant Attributes
    -----------
    """
    
    # Default Testfiles...!!! Not in use later

    # Path to altitude file -> TODO: Read paths from extern class
    #print(os.getcwd())
    bdir = os.path.dirname(__file__)
    #print(bdir)

    #html_tpl = os.path.join(bdir, 'data', 'template.html')
#    b = xr.open_rasterio(
#        'zip://E:\\Uni\\VU Wissenschaftliches Programmieren\\climvis-master\\climvis\\data\\srtm_39_03.zip!srtm_39_03.tif')
    #terrain_file = "zip://{}".format(os.path.join(bdir, 'data', 'srtm_39_03.zip!srtm_39_03.tif'))
    #print(terrain_file)
    terrain_file = os.path.join(bdir, 'data', 'srtm_39_03.zip')
    #print(terrain_file)

    # Path to weather data files
    weather_0degl_hourly_file = os.path.join(bdir, 'data', '0deg_level_hourly.nc')
    weather_precipitation_hourly_file = os.path.join(bdir, 'data', 'precipitation_hourly.nc')

    weather_0degl_daily_file = os.path.join(bdir, 'data', '0deg_level_daily.nc')
    weather_precipitation_daily_file = os.path.join(bdir, 'data', 'precipitation_daily.nc')
    weather_orography_file = os.path.join(bdir, 'data', 'orography.nc')
    
    # Default output folder
    # TODO: change os.getcwd to
    #print(os.getcwd())
    #output_folder =
    output_folder = "{}/output".format(os.getcwd())
    
    
class Skitour:
    """
    A class that calculates how likely you can do a given ski tour.

    ...

    Relevant Attributes
    ----------
    gps_data: class gps_track
        a instance of class gps_track who provide tour datas
    dataset: xarray
        snow and geo information for one position
    output_folder: string
        folder in which the output is stored

    Methods
    -------
    Public:
        pre_process_data():
            compresses the given hourly data into daily data
        calc_snow_data_for_track(gps_datas):
            calculate snow data for a given gps_track
        calc_snow_data_for_point(point):
            calculate snow data for a given gps_point
        calc_tour_data(date = dt.date.today()):
            calculate from snow conditions over the tour for a given date
        plot_snow_on_tour():
            plot the expected snow conditions on tour
        plot_snowheight_for_dataset(dataset):
            plot annual cycle of snowheight for a given snow dataset

    Private:
        _calc_terrain(dataset)
            calculate terrain informations for a given dataset
        _calc_slope(terrain_map, lon, lat):
            calculate slope informations for a given map and coordinates
        _calc_snowheight(dataset):
            calculate snowheights for a given dataset
        _load_weather_data(dataset):
            load weather data for a given dataset
        _calc_probability( point, date):
            calculated probability for snow on a given point and date
        _interpolate(x, xnew, data):
            interpolate on xnew between given y data
            
    Example using for Track:
        test_tour = Skitour(Data_Handler)
        test_tour.calc_snow_data_for_track(Gps_track)
        test_tour.calc_tour_data()
        test_tour.plot_snow_on_tour()
        
    Example using for point:
        snowpoint = Skitour(Data_Handler())
        coordinates = Gpx_point(lat, lon)
        snowpoint.calc_snow_data_for_point(coordinates)
        snowpoint.plot_snowheight_for_dataset(snowpoint.snow_data[0])
    """
    
    # Resolution of data TODO: Get resolutions from datasets
    resolution_altitude_file = 0.001  # ~3arcSeconds
    resolution_weather_data = 0.25

    # Initializer
    def __init__(self, data_files):
        """Set relevant attributes

        The initializer gets a datahandler class, who contains the relevant path to datafiles

        Parameters
        ----------
        data_files: class Data_handler

        Raises
        ------
        Exception
            If relevant data are not available
        """
        
        # Get relevant data
        try:
            if (os.path.isfile(data_files.terrain_file) and
                    os.path.isfile(data_files.weather_orography_file) and
                    os.path.isfile(data_files.weather_0degl_hourly_file) and
                    os.path.isfile(data_files.weather_precipitation_hourly_file)):
                
                # Set Path to terrain file
                #terrain_file = "zip://{}".format(os.path.join(bdir, 'data', 'srtm_39_03.zip!srtm_39_03.tif'))

                self.terrain_file = data_files.terrain_file
                #print(self.terrain_file)
                #self.terrain_file = "zip://{}{}".format(data_files.terrain_file,'!srtm_39_03.tif')
        
                # Set path to weather data files
                self.weather_orography_file = data_files.weather_orography_file
                self.weather_0degl_hourly_file = data_files.weather_0degl_hourly_file
                self.weather_precipitation_hourly_file = data_files.weather_precipitation_hourly_file
            else:
                raise FileNotFoundError
            
        except AttributeError and FileNotFoundError:
            raise Exception("Relevant data not avaible!")
    
        # If no daily datas avaibale -> pre_process_data()
        
        try:
            if (os.path.isfile(data_files.weather_0degl_daily_file) and
                    os.path.isfile(data_files.weather_precipitation_daily_file)):
                self.weather_0degl_daily_file = data_files.weather_0degl_daily_file
                self.weather_precipitation_daily_file = data_files.weather_precipitation_daily_file
            else:
                print("No hourly data found!")
                raise FileNotFoundError
                
        except AttributeError and FileNotFoundError:
            # Store data in main folder
            self.weather_0degl_daily_file = '0deg_level_daily.nc'
            self.weather_precipitation_daily_file = 'precipitation_daily.nc'
            
            self.pre_process_data()
        
        try:
            self.output_folder = data_files.output_folder
            #print(self.output_folder)
        except AttributeError:
            # Use default output_folder
            self.output_folder = "{}/output".format(os.getcwd())
        
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.snow_data = []  # A empty list who contained the snow_data for each point
    
    # Public Methods
    def pre_process_data(self):
        """Compress the given hourly data into daily data

        This is necessary, because I can only find ERA5 with a time resolution from one hour.
        But with a time resolution from a hour the following calculations needs too much time.
        So I try to take the daily average and the result are nearly the same.
        
        This methods load the given hourly weather data, calculate and save daily data.

        Parameters
        ----------
        none

        Raises
        ------
        none
        """
        
        print("Start preprocess data!")
        
        # Open Zero degree level, calculae mean over each day and save
        with xr.open_dataset(self.weather_0degl_hourly_file).load() as deg0l:
            daily_0degl = deg0l.deg0l_0001.resample(time='24H').mean('time')
            daily_0degl.to_netcdf(self.weather_0degl_daily_file)

        # Open total precipitation, calculate sum über each day and save
        with xr.open_dataset(self.weather_precipitation_hourly_file).load() as precipitation:
            daily_precipitation = precipitation.tp_0001.resample(time='24H').sum('time')
            daily_precipitation.to_netcdf(self.weather_precipitation_daily_file)

        print("Data are ready for usage.")
    
    def calc_snow_data_for_track(self, gps_data):
        """Calculate snow data for a given gps_track

        This method calculate snowdata for a given Gpx_Track
        over the time range from the given weather data

        Parameters
        ----------
        gps_data: class Gpx_track

        Raises
        ------
        none
        """

        self.gps_data = gps_data  # Write gps_data as atrribute for usage in other functions
        
        print("Starts snow calculations.")
        print("This will take a few seconds..")

        progress = 0  # Counter of the current progress of the calculations
        
        # Run over the list coordinate list in Gpx_track
        for counter, point in enumerate(self.gps_data.track):
            
            # Calculate snowheight for each position
            self.calc_snow_data_for_point(point)

            # Calculate and print progress in ten steps (Assumption: Each calculation needs the same time)
            if round((counter + 1) / len(self.gps_data.track) * 10) != progress:
                progress = round((counter + 1) / len(self.gps_data.track) * 10)
                print("{}%... finished".format(progress * 10))

        print("The snow calculations for these nice tour are ready!")
       
        
    def calc_snow_data_for_point(self, point):
        """Calculate snow data for a given gps_point

        This method calculate snowdata for a given Gpx_Point
        over the time range from the given weather data

        Parameters
        ----------
        point: class Gpx_point

        Raises
        ------
        none
        """
        
        # Create empty xarray "template" for snowdata -> all further data for the point are stored here
        dataset = xr.DataArray(np.empty(0, dtype=np.float32), coords=[[]], dims=["time"])
        
        # Write Positions as attributes
        dataset.attrs['lon'] = point.lon
        dataset.attrs['lat'] = point.lat

        # Calculate terrain informations for given point
        self._calc_terrain(dataset)
        
        # Test if these point is equal to an existing point -> Save time
        # If Gpx point have similar propertys to an old point use snowdata from old point and return
        for i in self.snow_data:
            
            # Similar propertys: differenz of height < 100 -> Later test if slope propertys is also similar
            # Also test if point was a new snow calculation
            if np.isclose(i.map_height, dataset.map_height, atol=100) and i.isCalculated is True:
                dataset.attrs["isCalculated"] = False  # Mark that this point is not a new calculation
                self.snow_data.append(xr.concat([dataset, i], dim="time"))  # Take snow data from similiar point
                return
        
        # Calculate snowheight for the given point
        self.snow_data.append(self._calc_snowheight(dataset))
        
    def calc_tour_data(self, date=dt.date.today()):
        """Calculate from snow conditions over the tour for a given date
        
        This method works only if the method calc_snow_data_for_track() was called before.

        Parameters
        ----------
        date: datetime -> default: today

        Raises
        ------
        Exception
            If no sound is set for the animal or passed in as a
            parameter.
        """
        
        # If no snow data is available, throw an error
        if self.snow_data == []:
            raise Exception('No snowdata exist for calculating snow conditions! Try to run calc_data_for_track() first!')
            
        print("Start tour calculations.")

        # Empty Container for data
        snow_mean = np.empty(len(self.snow_data), dtype=np.float32)  # Array for all averages of snowheight on tour
        snow_probability = np.empty(len(self.snow_data), dtype=np.float32)  # Array for all snow probabilitys on tour
        
        # Run over all points from the given track
        for counter, point in enumerate(self.snow_data):
            
            # Calculate snow probability for each given point
            self._calc_probability(point, date)

            # Write mean snow and probability for each position in array
            snow_mean[counter] = point.snow_mean
            snow_probability[counter] = point.probability
    
        # Print and write snow conditions of the tour
  
        with open("{}/Tour_Infos.txt".format(self.output_folder), "w") as f:
            # message = "The predicted average snow depth is {}cm.\n".format(int(snow_mean.mean()))
            # print(message)
            # f.writelines(message)
            
            if(snow_probability.min() < 1):
                message = ":( The calculated probability for skiing is less then 1%. But heey, never give up!\n"
                print(message)
                f.writelines(message)
            elif(snow_probability.min() > 99):
                message = ":D The calculated probability for skiing is higher then 99%. Run Forest, run!\n"
                print(message)
                f.writelines(message)
            else:
                message = "With a calculated probability of {}% skiing on {} is possible on this tour.\n".format(snow_probability.min(), date)
                print(message)
                f.writelines(message)
            f.close()
            
            return message

    def plot_snow_on_tour(self, annual_cycle=True):
        """Plot the expected snow conditions on tour

        This method plots the probability for skiing along the tour.
        If desired, the annual expected snow depth for the location with the least snow is also plotted.
        The picture stored in a folder with name "plots"
        
        This method works only if the method calc_snow_data_for_track() was called before.
        This method works only if the method calc_tour_data() was called before.

        Parameters
        ----------
        annual_cycle: Boolean default=True

        Raises
        ------
        Exception
            If necessary data could not be loaded from stored data
        """
        
        # Container for tour data to be plotted
        tour_snow_prob = []
        tour_altitude = []
        
        # Set smoothing factor for plots
        smoothing_factor = 5

        # Get TourData
        try:
            # Run over all data points
            for i in self.snow_data:
                tour_snow_prob.append(i.probability)
                tour_altitude.append(i.map_height)
        except AttributeError:
            raise Exception("Necessary data could not be loaded. Try to run calc_tour_data first.")

        # Set x Values from 0 to total Distance of the tour
        x = np.linspace(0, self.gps_data.tot_dist(), len(tour_altitude))
        
        # Smooting altitude data with given smoothing factor
        y = gaussian_filter1d(tour_altitude, sigma=smoothing_factor)

        # Create two-dimensional array with data for color lines
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Create plot
        fig, axs = plt.subplots()

        # Create a continuous norm to map from data points to colors (0% = red, 100% = green)
        normalize = plt.Normalize(0, 100)
        lc = LineCollection(segments, cmap='RdYlGn', norm=normalize)  # RdYlGn -> Farbpalette

        # Set the values used for colormapping
        color = gaussian_filter1d(tour_snow_prob, sigma=smoothing_factor)
        lc.set_array(np.array(color))
        lc.set_linewidth(3)
        line = axs.add_collection(lc)
        
        # Add colorbar with label
        cbar = fig.colorbar(line, ax=axs)
        cbar.set_label('Probability for skiing', rotation=270)

        # Plot Settings
        axs.set_xlim(x.min(), x.max())
        axs.set_ylim(y.min() - 50, y.max() + 50)
        plt.title("Skiing conditions on {}".format(self.snow_data[0].date.strftime("%d-%m-%Y")))
        plt.ylabel("Altitude in m")
        plt.xlabel("Distance in km")
        
        # Save fig in output_folder
        save_dir = plt.savefig("{}/snow_on_tour.png".format(self.output_folder))
        #print(save_dir)
        
        if annual_cycle is True:
            
            # Plot the average annual snow depth for the found location with the lowest snow depth on the tour.
            for i in self.snow_data:
                if np.isclose(i.probability, np.array(tour_snow_prob).min()):
                    self.plot_snowheight_for_dataset(i)
                    break
       
    
    def plot_snowheight_for_dataset(self, dataset):
        """Plot annual cycle of snowheight for a given snow dataset

        This method plot the expected snowheight over a year for a location based on the stored data in dataset
        The picture stored in a folder with name "plots".

        Parameters
        ----------
        dataset: xarray

        Raises
        ------
        """

        # Calculate monthly data
        s_mean = dataset.groupby("time.month").mean()
        s_max = dataset.groupby("time.month").max()
        s_min = dataset.groupby("time.month").min()
        s_std = dataset.groupby("time.month").std()

        # Set Month as x Values
        x = range(0, 12)

        # Calculate 1-sigma area
        s_1sigma_t = s_mean + s_std
        s_1sigma_b = s_mean - s_std
        s_1sigma_b[s_1sigma_b < 0] = 0

        # Create line for minimum Snowheight for a Skitour at 30cm -> TODO: Dependent on surface propertys (stone, gras, etc. )
        snow_minimum = np.full(shape=len(x), fill_value=30, dtype=np.int)
        
        # Create a zero line for filling area between zero and 30cm line
        zero_line = np.zeros(shape=len(x))

        # New x Values for interpolate functions
        xnew = np.linspace(0, 11, num=100, endpoint=True)

        # Acronyms for x axes label
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']

        # Plot lines
        plt.plot(xnew, self._interpolate(x, xnew, s_mean), label='Mean')
        plt.plot(xnew, self._interpolate(x, xnew, s_max), label='Maximum', color='seagreen')
        plt.plot(xnew, self._interpolate(x, xnew, s_min), label='Minimum', color='firebrick')
        plt.plot(xnew, self._interpolate(x, xnew, s_1sigma_t), label='1-Sigma', linestyle='--', color='seagreen')
        plt.plot(xnew, self._interpolate(x, xnew, s_1sigma_b), linestyle='--', color='firebrick')
        plt.plot(months, snow_minimum, label='Min. Skitour', linestyle='dotted')

        # Add plot infos
        plt.legend()
        plt.xlim(0, 11)
        plt.ylim(0, max(100, max(self._interpolate(x, xnew, s_max)) + 20))
        plt.title("Yearly snowheight for {}°N, {}°E, {}m".format(round(dataset.lat, 2), round(dataset.lon, 2), round(dataset.map_height)))
        plt.fill_between(xnew, self._interpolate(x, xnew, s_1sigma_t), self._interpolate(x, xnew, s_1sigma_b), color='grey', alpha=0.3)
        plt.fill_between(months, snow_minimum, zero_line, color='firebrick', alpha=0.3)
        plt.xlabel("Month")
        plt.ylabel("Snowheight in cm")
        plt.grid(True)
        
        # Save fig in plot_folder
        plt.savefig("{}/snowheight.png".format(self.output_folder))
        #print("{}/snowheight.png".format(self.output_folder))

    # Private Methods
    def _calc_terrain(self, dataset):
        """Calculate terrain informations for a given dataset

        This method calculate for a given point different propertys of the terrain (height, slope, direction).
        TODO: Get Informations about the surface (stone, grass etc.)

        Parameters
        ----------
        dataset: xarray

        Raises
        ------
        Exception
            If altitude data file can not load
        IndexError
            If point is not in range of altitude data
        """
        
        # Open altitude map and get height of the point
        try:
            # Load terrain map only, when not loaded before
            if hasattr(self, 'terrain') is False:
                # 'zip:data/srtm_39_03.zip!srtm_39_03.tif'
                file_name = os.path.basename(self.terrain_file)
                tif_name = file_name.replace("zip", "tif")
                terrain_file = 'zip:{}!{}'.format(self.terrain_file, tif_name)
                self.terrain_map = xr.open_rasterio(terrain_file)

                #terrain_file = "zip://{}!{}".format(self.terrain_file, 'srtm_39_03.tif')
                #self.terrain_map = xr.open_rasterio(terrain_file)
        except KeyError:
            Exception("{} data cannot be loaded.".format(terrain_file))

        # Search nearest point on map
        point_on_map = self.terrain_map.sel(x=dataset.lon, y=dataset.lat, method="nearest")
              
        # Test if distance from map-point to given point is higher then the resolution of the map
        # != True vs is not True -> first version works, second not!?!?wtf
        if (np.isclose(float(point_on_map.x), dataset.lon, atol=self.resolution_altitude_file) and np.isclose(float(point_on_map.y), dataset.lat, atol=self.resolution_altitude_file)) != True:
            raise IndexError('Coordinates {}°N and {}°E can not found in altitude file! '.format(dataset.lat, dataset.lon))
            
# =============================================================================
#         # Calculate slope propertys
#         # Not in use yet -> Important for independet of solar radiation
#         slope = self._calc_slope(self.terrain_map, dataset.lon, dataset.lat)
#         
#         # Write attributes
#         dataset.attrs['slope'] = slope[0]
#         dataset.attrs['direction'] = slope[1]
# =============================================================================
        
        dataset.attrs['map_lon'] = float(point_on_map.x)
        dataset.attrs['map_lat'] = float(point_on_map.y)
        dataset.attrs['map_height'] = int(point_on_map)
        
        return dataset

# =============================================================================
#     def _calc_slope(self, terrain_map, lon, lat):
#         """Calculate slope informations for a given map and coordinates
#         
#         Not in Use yet !!! -> Alpha phase
# 
#         This method calculate the slope and the direction for given coordinates on a altitude file
# 
#         Parameters
#         ----------
#         terrain_map: xarray
#         lon: float
#         lat: float
# 
#         Raises
#         ------
#         none
#         """
# 
#         # ***TODO! Reaaally ugly yet.***
# 
#         # Container for points of altitude around the position (env=enviroment)
#         env = np.empty((3, 3), dtype=np.int)
# 
#         # Get points of altitude around the position
#         for i in range(-1, 2):
#             for j in range(-1, 2):
#                 env[i + 1, j + 1] = terrain_map.sel(x=(lon + (j * terrain_map.res[0])), y=lat - (i * terrain_map.res[1]), method="nearest")
# 
#         # Container for altitude gradients
#         gradients = []
# 
#         # Loop over the enviroment ->   ***
#         #                               *x*
#         #                               ***
#         # Try to calculate 4 single slope and middle at the end
#         for m in [0, 1]:
#             for n in [0, 1]:
#                 try:
#                     # Calculate NorthSouth gradient
#                     y_gradient = ((env[0 + m, 0 + n] - env[1 + m, 0 + n]) + (env[0 + m, 1 + n] - env[1 + m, 1 + n])) / 2
#                     # Calculate EastWest gradient
#                     x_gradient = ((env[0 + m, 0 + n] - env[0 + m, 1 + n]) + (env[1 + m, 0 + n] - env[1 + m, 1 + n])) / 2
#                     gradients.append([y_gradient, x_gradient])
#                 except IndexError:  # For example on the edge of the map
#                     continue
# 
#         # Mean of the gradients
#         st = (np.array(gradients)).mean(axis=0)
# 
#         # Calculate Resolution of the map in meters depending on the degree of latitude
#         res_lat = (6371000 * 2 * np.pi) / (360 / terrain_map.res[0])
#         res_lon = (np.cos(abs(lat) * np.pi / 180) * 6371000 * 2 * np.pi) / (360 / terrain_map.res[0])
# 
#         # Calculate the slopes in degree
#         slope_north = np.arctan(st[0] / res_lat) * 180 / np.pi
#         slope_east = np.arctan(st[1] / res_lon) * 180 / np.pi
# 
#         # Calculate the maximum slope for position
#         slope_max = max(abs(slope_north), abs(slope_east))
# 
#         # divide into four qudrants
#         if slope_east >= 0 and slope_north <= 0:
#             faktor_n = 0
#             faktor_o = 90
#         elif slope_east >= 0 and slope_north >= 0:
#             faktor_n = 180
#             faktor_o = 90
#         elif slope_east <= 0 and slope_north <= 0:
#             faktor_n = 360
#             faktor_o = 270
#         else:  # slope_east <= 0 and slope_north >= 0:
#             faktor_n = 180
#             faktor_o = 270
# 
#         # Calculate the direction from the relation of slopes
#         direction = (abs(slope_north) * faktor_n + abs(slope_east) * faktor_o) / (abs(slope_north) + abs(slope_east))
# 
#         return slope_max, direction
# =============================================================================

    def _calc_snowheight(self, dataset):
        """Calculate snowheights for a given dataset

        This method calculate the snowheight over the given weather data for a dataset.
        As a minimum, the data zero degree greze, absolute precipitation and orography are required.
        In the next step, wind, solar radiation, humidity and temperature are to be considered.
        

        Parameters
        ----------
        dataset: xarray

        Raises
        ------
        IndexError
            If weather data are not completely
        """
        
        # Open weather data
        self._load_weather_data(dataset)

        # Create Empty in size of weather data XArray
        # TODO: Not ready yet. Temporarily take over time scale of precipitation data.
        snowheight = xr.DataArray(np.empty(self.p_local.size, dtype=np.float32), coords=[self.p_local.time], dims=["time"])

        # Get Modell height for location
        modell_height = int(self.oro_local[0])

        # This variable store the current snowheight
        s_sum = 0
        
        for idx in range(min(self.p_local.size, self.d_local.size)):  # TODO vielleicht eine Möglichkeit schöner mit zip()?
            try:
                # assert p_local.time[idx] == d_local.time[idx], "Non equal timestemps" # TODO: Dauert 6mal länger!!!??

                # Calculate differenz[m] between zero degree level und height of location
                diff = dataset.map_height - (float(self.d_local[idx]) + modell_height)

                # if zero degree level is more the 200m heigher as the location -> Snowfall
                # else -> melting
                if diff > -200 or np.isclose(dataset.map_height - modell_height, diff, atol=10):
                    s_sum = s_sum + float(self.p_local[idx]) * 1000  # Percipitation in cm Snow
                else:
                    s_sum = s_sum + (diff / 100.) * 0.05 * 24  # Simple Snow melting faktor... -> TODO: Melting dependent on temperatur, radiation, wind
                s_sum = max(s_sum, 0)  # Min 0cm Snow
               
                snowheight[idx] = s_sum
    
                # Schönerer Variante aber extrem langsam
                # new = xr.DataArray([s_sum], coords=[[dt.datetime(2020, 5, 18)]], dims=["time"])
                # snowheight = xr.concat([snowheight, new], dim="time")

            except IndexError:
                raise Exception("Error with weather data!!!")

        # Concat snow data to dataset
        dataset = xr.concat([dataset, snowheight], dim="time")

        # Add Attributes
        dataset.attrs['modell_height'] = modell_height
        dataset.attrs["isCalculated"] = True  # Mark that this point is a new calculation
        
        return dataset
    
    def _load_weather_data(self, dataset):
        """Load weather data for a given dataset

        This method load all necessary weather data for a given dataset.
        Start time and end time as well as the number of time points are stored as attributes.

        Parameters
        ----------
        dataset: xarray

        Raises
        ------
        IndexError
            If position can not found in weatherfiles
        Exception
            If the start times of the weather data are not the same
        none
        """
        
        # Open weather data, when not opened before
        if hasattr(self, 'zeroDegree') is False:
            self.zeroDegree = xr.open_dataset(self.weather_0degl_daily_file).load()
        if hasattr(self, 'precipitation') is False:
            self.precipitation = xr.open_dataset(self.weather_precipitation_daily_file).load()
        if hasattr(self, 'orography') is False:
            self.orography = xr.open_dataset(self.weather_orography_file).load()

        # Get Modelldata for location
        self.oro_local = self.orography.z.sel(longitude=dataset.lon, latitude=dataset.lat, method="nearest") / 9.81
                
        # Test if distance from map-point to given point is higher then the resolution of the map
        # != True vs is not True -> first version works, second not!?!?wtf
        if (np.isclose(float(self.oro_local.longitude), dataset.lon, atol=self.resolution_weather_data) and np.isclose(float(self.oro_local.latitude), dataset.lat, atol=self.resolution_weather_data)) != True:
            raise IndexError('Coordinates {}°N and {}°E can not found in {}!'.format(dataset.lat, dataset.lon, self.weather_orography_file))
        
        # The follwing code is only necessary because the Zero-Degree-Level from the ERA5 Data is Null, when the Zero Degree Level is on the same height as the orography.
        # That is the case, when the whole atmosphere has a temperature under 0°C
        # the problem now is, if in the resolution of the weather data a point exists which lies clearly deeper than the model orography,
        # a zero degree limit which indicates zero, cannot be determined whether at the deeper point also frost is.
        # Therefore, I search in the environment around the point, a point in the weather model that is as low as possible.
        
        # If the modell height is heigher as the given point
        if int(self.oro_local[0]) > dataset.map_height:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    tmp = self.orography.z.sel(longitude=dataset.lon + (i * 0.25), latitude=dataset.lat + (j * 0.25), method="nearest") / 9.81
                    # If the new modell height is lower -> select this point
                    if int(tmp[0]) < int(self.oro_local[0]):
                        self.oro_local = tmp

        # Select the grid point where the model orography is as deep as possible for zeroDegreeLevel
        self.d_local = self.zeroDegree.deg0l_0001.sel(longitude=float(self.oro_local.longitude), latitude=float(self.oro_local.latitude), method="nearest")
        
        # Test if distance from map-point to given point is higher then the resolution of the map
        # != True vs is not True -> first version works, second not!?!?wtf
        if (np.isclose(float(self.d_local.longitude), float(self.oro_local.longitude), atol=self.resolution_weather_data) and np.isclose(float(self.d_local.latitude), float(self.oro_local.latitude), atol=self.resolution_weather_data)) != True:
            raise IndexError('Coordinates {}°N and {}°E can not found in {}!'.format(float(self.oro_local.latitude), float(self.oro_local.longitude), self.weather_0degl_daily_file))
        
        # Select nearest percipitation grid point
        self.p_local = self.precipitation.tp_0001.sel(longitude=dataset.lon, latitude=dataset.lat, method="nearest")
        
        # Test if distance from map-point to given point is higher then the resolution of the map
        # != True vs is not True -> first version works, second not!?!?wtf
        if (np.isclose(float(self.p_local.longitude), dataset.lon, atol=self.resolution_weather_data) and np.isclose(float(self.p_local.latitude), dataset.lat, atol=self.resolution_weather_data)) != True:
            raise IndexError('Coordinates {}°N and {}°E can not found in {}!'.format(dataset.lat, dataset.lon, self.weather_precipitation_daily_file))

        # Test if data starts at same date
        if self.p_local.time[0] != self.d_local.time[0]:
            raise Exception("The beginning Time of weather data are not equal!")
            
        # TODO finde gemeinsamen Anfangs und Endzeitpunkt

    def _calc_probability(self, point, date):
        """Calculated probability for snow on a given point and date

        This method calculate from stored snow_datas propertys and probability of the snow cover
        for a give point and date.

        Parameters
        ----------
        point: class Gpx_point
        date: datetime

        Raises
        ------
        none
        """

        # Select data of today from all years
        new = point.where(point.time.dt.day == date.day)
        new = new.where(point.time.dt.month == date.month)
        new = new.dropna(dim="time", how='any')

        # Calculate snow propertys
        today_mean = new.mean()
        today_min = new.min()
        today_max = new.max()
        today_std = new.std()

        # Calculate probability for minimum 30cm snow
        if today_std > 0:  # TODO Mittelwert > 0 aber Standardabweichung = 0
            today_prob = round((1 - norm.cdf(30, today_mean, today_std)) * 100)
        else:
            today_prob = 0

        # Add attributes to snow data
        point.attrs['date'] = date
        point.attrs['snow_minimum'] = today_min
        point.attrs['snow_maximum'] = today_max
        point.attrs['snow_mean'] = today_mean
        point.attrs['probability'] = today_prob
        
    # Utilities
    def _interpolate(self, x, xnew, data):
        """Interpolate on xnew between given y data

        This method makes a cubic interpolation of the data on xnew.

        Parameters
        ----------
        x: float array
        xnew: float array
        data: float array

        Raises
        ------
        none
        """
        cubic = interp1d(x, data, kind='cubic')
        ynew = cubic(xnew)
        ynew[ynew < 0] = 0
        return ynew

# directory = mkdtemp() 
# print(directory)
# test = Data_Handler()
# test.output_folder = directory

# print(test.output_folder)