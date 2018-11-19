# A climate visualization package

**climvis** offers command line tools to display climate data in your browser.

It was written for the University of Innsbruck's
[scientific programming](http://fabienmaussion.info/scientific_programming)
lecture as a package template for the assignments.

## HowTo

Make sure you have all dependencies installed. These are:
- numpy
- pandas
- xarray
- motionless
- matplotlib

Download the package and install it development mode. From the root directory,
do:

    $ pip install -e .

If you are on a university computer, you should use:

    $ pip install --user -e .

## Command line interface

``setup.py`` defines an "entry point" for a script to be used as a
command line program. Currently, the only command installed is ``cruvis``.

After installation, just type:

    $ cruvis --help

To see what it can do for you.

## Testing

I recommend to use [pytest](https://docs.pytest.org) for testing. To test
the package, do:

    $ pytest .

From the package root directory.


## License

With the exception of the ``setup.py`` file which was adapted from the
[sampleproject](https://github.com/pypa/sampleproject) package, all the
code in this repository is dedicated to the public domain.
