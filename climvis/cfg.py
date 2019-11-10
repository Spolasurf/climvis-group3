"""This configuration module is a container for parameters and constants."""
import os

cru_dir = '/home/mowglie/disk/TMP_Data/CRU/'
cru_tmp_file = cru_dir + 'cru_ts4.03.1901.2018.tmp.dat.nc'
cru_pre_file = cru_dir + 'cru_ts4.03.1901.2018.pre.dat.nc'
cru_topo_file = cru_dir + 'cru_cl1_topography.nc'

bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, 'data', 'template.html')
world_cities = os.path.join(bdir, 'data', 'world_cities.csv')

default_zoom = 8
