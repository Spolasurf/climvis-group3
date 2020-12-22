"""This configuration module is a container for parameters and constants."""
import os
import sys
from pathlib import Path

path = "{}/.climvis".format(str(Path.home()))

# TODO: we could write a test for this: like if .climvis doesnt
# exist if it creates a new .climvis file

# Try opening the file where the path is stored or ask to create one with correct path
try:
    file = open(path, 'r')  # open file in read
    cru_dir = file.readline()
    file.close()

except FileNotFoundError:
        print("File {} wird angelegt.".format(path))
        defaultPath = input("Please enter the Directory to the CRU files: ")
        file = open(path, 'w+')
        file.write(defaultPath)
        file.close()
        cru_dir = defaultPath

# Add other file paths and create list containing all paths
cru_tmp_file = cru_dir + 'cru_ts4.03.1901.2018.tmp.dat.nc'
cru_pre_file = cru_dir + 'cru_ts4.03.1901.2018.pre.dat.nc'
cru_topo_file = cru_dir + 'cru_cl1_topography.nc'

filespath = [cru_tmp_file,cru_pre_file,cru_topo_file]

# Check if all files are availabe in the given paths. If not stop script
for i in filespath:
    if Path(i).is_file() is False:
        print("The CRU files are not available on this system. For cruvis (part of the climvis package) to work properly, please create a file called '.climvis' in your HOME directory, and indicate the path to the CRU directory in it.")
        print("***Stop script***")
        sys.exit()

# Make path to website template and "world cities coordinates file"
bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, 'data', 'template.html')
world_cities = os.path.join(bdir, 'data', 'world_cities.csv')

default_zoom = 8