import webbrowser
import sys
import os
import climvis
#from climvis import cfg

from climvis.gpx_reader import Gpx_track
#from climvis.gpx_reader import Gpx_point
from climvis.Skitour import Data_Handler, Skitour

from tempfile import mkdtemp
import datetime as dt

#from inspect import getmembers, isfunction

#from somemodule import foo
#print(getmembers(climvis, isfunction))

# from climvis.snowheight import tour
# tour(asdf)

#import os
#sys.path.append("E:\\Uni\\VU Wissenschaftliches Programmieren\\climvis-master\\climvis")
#import tour
#import snowheight1
#from climvis import snowheight
#from snowheight1 import tour

HELP = """cruvis: CRU data visualization at a selected location.

Usage:
   -h, --help            : print the help
   -v, --version         : print the installed version
   -l, --loc [LON] [LAT] : the location at which the climate data must be
                           extracted
   --no-browser          : the default behavior is to open a browser with the
                           newly generated visualisation. Set to ignore
                           and print the path to the html file instead
"""


def cruvis_io(args):
    """The actual command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    if len(args) == 0:
        print(HELP)
    elif args[0] in ['-h', '--help']:
        print(HELP)
    elif args[0] in ['-v', '--version']:
        print('cruvis: ' + climvis.__version__)
        print('License: public domain')
        print('cruvis is provided "as is", without warranty of any kind')
    elif args[0] in ['-l', '--loc']:
        if len(args) < 3:
            print('cruvis --loc needs lon and lat parameters!')
            return
        lon, lat = float(args[1]), float(args[2])
        html_path = climvis.write_html(lon, lat)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)
    else:
        print('cruvis: command not understood. '
              'Type "cruvis --help" for usage options.')


def cruvis():
    """Entry point for the cruvis application script"""

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)
    #print(sys.argv[1:]) # ['-l', '14', '48', '--no-browser']
    cruvis_io(sys.argv[1:])

def snowheight_io(args):
    """The actual command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    if len(args) == 0:
        print(HELP)
    elif args[0] in ['-h', '--help']:
        print(HELP)
    elif args[0] in ['-v', '--version']:
        print('snowheight: ' + climvis.__version__)
        print('License: public domain')
        print('snowheight is provided "as is", without warranty of any kind')

    # Snowheight location/position option
    elif args[0] in ['-l', '--loc']:
        if len(args) < 3:
            print('snowheight --loc needs lon and lat parameters!')
            return
        #date = str(args[1])
        lon, lat = float(args[1]), float(args[2])

        #lon = 11
        #lat = 47


        point = (lon, lat)

        # Check if Latitude and Longitude are in the correct range for the precipitation and temperature data
        if lat < 45 or lat > 50:
            raise Exception('Location is out of the permitted range lon = [10, 15] lat = [45, 50]! Analysis not possible')
        elif lon < 10 or lon > 15:
            raise Exception('Location out of the permitted range lon = [10, 15] lat = [45, 50]! Analysis not possible')
        else:
            pass


        #the_tour.calc_snow_data_for_track(user_track)
        #test = dt.datetime.strptime(date, '%d.%m.%Y')
        #msg = snowpoint.calc_tour_data(test)
        #snowpoint.plot_snow_on_tour()

        # creation of the html path for the track -> see core.py
        #print(climvis.modules)
        #print(dir())


        html_path = climvis.write_point_html(point)

        #print(sys.path)
        #print(os.listdir("E:\\Uni\\VU Wissenschaftliches Programmieren\\climvis-master\\climvis"))



        #loc1= Skitour()
        #loc1 = climvis.snowheight.tour(loc)
        #print(loc.__class__)
        #loc1.calc_datas()
        #loc1.calc_tour()


        #loc.climvis.snowheight.tour.calc_datas()
        #loc.climvis.snowheight.tour.calc_tour()

#        html_path = climvis.write_html(lon, lat)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)


    # Snowheight town option
    elif args[0] in ['-t', '--town']:
        if len(args) != 2 or not args[1].replace('.','',1).isdigit() and args[1].replace('.','').isdigit()\
                or args[1].replace('.','').isdigit():
            raise Exception('snowheight -t needs a town as an Input')
        point = args[1]
        html_path = climvis.write_point_html(point)

        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)

        print(point)

        print('this is location function')

    # Snowheight gpx file option
    elif args[0] in ['-g', '--gpx']:
        if len(args) < 3:
            print('cruvis --gpx needs the date (dd-mm-yyyy) and the name of the .gpx file ')
            return
        # sets the date for when the calculations should be done
        date = str(args[1])
        # variable with the user input name of the .gpx tour
        gpx_file_name = str(args[2])
        # assuming the .gpx file is in .\cruvis\data directory as given by installation package
        bdir = os.path.dirname(__file__)
        gpx_file_path = os.path.join(bdir, 'data', gpx_file_name)  # os.path.abspath(gpx_file_name)#MAYBE TO CHANGE?
        # checks if gpx_file_path actually exists
        if os.path.isfile(gpx_file_path):
            pass
            #gpx_file_path = gpx_file_path
            # if it does not exist, asks for the full path on the pc from the user
        else:
            print('File not found in cwd!')
            gpx_file_path = input('Please give whole path to gpx file: ')
            if os.path.isfile(gpx_file_path):
                #gpx_file_path = gpx_file_path
                gpx_file_name = os.path.basename(gpx_file_path)
                #gpx_file_path = os.path.basename(gpx_file_path)
                # if still not correct, shuts the program down
            else:
                raise Exception('File does not exist! Program will shut down')

                # the track in the .gpx file is used to create a Gpx_track() instance named user_track
        user_track = Gpx_track(gpx_f_path=gpx_file_path)
        user_track.extract_gpx_points()

        # the lat and lon range is checked to ensure the track is contained in range for which the program has the climate data
        for i in user_track.track:
            if i.lat < 45 or i.lat > 50:
                raise Exception('Some trackpoints are out of the permitted range lon = [10, 15] lat = [45, 50]! Analysis not possible')
            elif i.lon < 10 or i.lon > 15:
                raise Exception('Some trackpoints are out of the permitted range lon = [10, 15] lat = [45, 50]! Analysis not possible')
            else:
                pass

        # the mean (lat,lon) coordinates of the track are extracted to center the map on the track, default zoom of map is 13
        pt_mean = user_track.get_mean()
        lat_mean = pt_mean[0]
        lon_mean = pt_mean[1]

        # the temporary directory to store the files and html path is created
        temp_directory = mkdtemp()

        # instance of the Data_Handler() class is created with the paths to the climate data
        # and the output folder is set to the just created temp_directory
        data = Data_Handler()
        data.output_folder = temp_directory
        # instance of Skitour() is created and the calcuations for the expected snow on the
        # user input desired date are processed and saved in temp_directory
        the_tour = Skitour(data)
        the_tour.calc_snow_data_for_track(user_track)
        test = dt.datetime.strptime(date, '%d.%m.%Y')
        msg = the_tour.calc_tour_data(test)
        the_tour.plot_snow_on_tour()

        # creation of the html path for the track -> see core.py
        #print(climvis.modules)
        #print(dir())
        html_path = climvis.write_track_html(gpx_file_path, lat_mean, lon_mean, gpx_name=gpx_file_name, mesg=msg,
                                            directory=temp_directory)

        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)
    else:
        print('cruvis: command not understood. '
              'Type "cruvis --help" for usage options.')


def snowheight():
    """Entry point for the cruvis application script"""

    #print("Welcome to the Snowheight calculator")
    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)
    #print(sys.argv[1:]) # ['-l', '14', '48', '--no-browser']
    snowheight_io(sys.argv[1:])
