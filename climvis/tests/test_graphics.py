import os
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from climvis import core, cfg, graphics


def test_annual_cycle(tmpdir):

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]
    df = core.get_cru_timeseries(dfi.Lon, dfi.Lat)

    fig = graphics.plot_annual_cycle(df)

    # Check that the text is found in figure
    ref = 'Climate diagram at location (11.25°, 47.25°)'
    test = [ref in t.get_text() for t in fig.findobj(mpl.text.Text)]
    assert np.any(test)

    # Check that figure is created
    fpath = str(tmpdir.join('annual_cycle.png'))
    graphics.plot_annual_cycle(df, filepath=fpath)
    assert os.path.exists(fpath)

    plt.close()
