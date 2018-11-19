"""This configuration module is a container for parameters and constants."""
import os

cru_dir = '/home/mowglie/disk/OGGM_INPUT/cru/'
cru_tmp_file = cru_dir + 'cru_ts4.01.1901.2016.tmp.dat.nc'
cru_pre_file = cru_dir + 'cru_ts4.01.1901.2016.pre.dat.nc'
cru_topo_file = cru_dir + 'cru_cl1_topography.nc'

bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, 'data', 'template.html')
world_cities = os.path.join(bdir, 'data', 'world_cities.csv')

default_zoom = 8
