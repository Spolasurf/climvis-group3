# A climate visualization and a snowheight calculator package

**climvis** offers command line tools to display climate data aswell as snowheight for locations or tracks in your browser.

It was written for the University of Innsbruck's
[scientific programming](http://fabienmaussion.info/scientific_programming)
lecture as a package template for the assignments.
This version has been modified and extended by students of said lecture.

## HowTo

Make sure you have all dependencies installed. These are:
- numpy
- pandas
- xarray
- motionless
- matplotlib
- geopy
- gpxpy

Download the package and install it development mode. From the root directory,
do:

    $ pip install -e .

If you are on a university computer, you should use:

    $ pip install --user -e .

## Command line interface

``setup.py`` defines an "entry point" for a script to be used as a
command line program. Currently, there are two commands installed:
The ``cruvis`` command line provides climate visualisation for specified locations, 
whilest ``snowheight`` calculates the probability for snow at a given location or track.

After installation, just type:

    $ cruvis --help

or

    $ snowheight --help

To see what it can do for you.

## Testing

I recommend to use [pytest](https://docs.pytest.org) for testing. To test
the package, do:

    $ pytest .

From the package root directory.

## Authors

Fabien Maussion:
- original climvis package with ``cruvis`` command

Laurin Steinmaier:
- Skitour.py (class Data_Handler edited by Sebastian)
- test_Skitour.py

Rebecca Chizzola:
- gpx_reader.py
- test_gpx_reader.py
- core.py: snowheight -g, GPXHandler, get_googlemap_track_url, write_track_html
- test_core.py: test_GPXHandler, test_get_google_track_url, test_write_track_html

Sebastian Dobesberger:
- Guided exercises
- Putting All files into the climvis package and make it one working package
- Pep8 edit: about 200 lines in All files
- cli.py Adding every other snowheight commands (all other than snowheight -g)
- test_cli.py
- core.py: write_html (guided exercise), write_point_html
- test_core.py: test_write_point_html, test_error_write_point_html

## License

With the exception of the ``setup.py`` file which was adapted from the
[sampleproject](https://github.com/pypa/sampleproject) package, all the
code in this repository is dedicated to the public domain.
