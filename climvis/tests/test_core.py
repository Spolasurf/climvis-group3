from urllib.request import Request, urlopen
import json
import os
import numpy as np
import pandas as pd

from climvis import core, cfg


def test_get_ts():

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]

    df = core.get_cru_timeseries(dfi.Lon, dfi.Lat)
    assert df.grid_point_elevation > 500  # we are in the alps after all
    assert df.distance_to_grid_point < 50000  # we shouldn't be too far

    # It's different data but I wonder how we compare to the
    # Innsbruck climate station we studied a couple of weeks ago?
    url = ('https://raw.githubusercontent.com/fmaussion/'
           'scientific_programming/master/data/innsbruck_temp.json')
    req = urlopen(Request(url)).read()

    # Read the data
    data = json.loads(req.decode('utf-8'))
    for k, v in data.items():
        data[k] = np.array(data[k])

    # select
    t = data['TEMP'][np.nonzero((data['YEAR'] <= 2016))]
    yrs = data['YEAR'][np.nonzero((data['YEAR'] <= 2016))]
    dfs = df.loc[(df.index.year >= yrs.min()) &
                 (df.index.year <= yrs.max())].copy()
    assert len(dfs) == len(yrs)
    dfs['ref'] = t
    dfs = dfs[['tmp', 'ref']]

    # Check that we have good correlations at monthly and annual scales
    assert dfs.corr().values[0, 1] > 0.95
    assert dfs.groupby(dfs.index.year).mean().corr().values[0, 1] > 0.9

    # Check that altitude correction is helping a little
    z_diff = df.grid_point_elevation - dfi.Elevation
    dfs['tmp_cor'] = dfs['tmp'] + z_diff * 0.0065
    dfm = dfs.mean()
    assert np.abs(dfm.ref - dfm.tmp_cor) < np.abs(dfm.ref - dfm.tmp)


def test_get_url():

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]

    url = core.get_googlemap_url(dfi.Lon, dfi.Lat)
    assert 'maps.google' in url


def test_write_html(tmpdir):

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]

    dir = str(tmpdir.join('html_dir'))
    core.write_html(dfi.Lon, dfi.Lat, directory=dir)
    assert os.path.isdir(dir)
