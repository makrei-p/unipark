import pandas as pd
import geopandas
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import numpy as np


def get_geopandas_world():
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world.at[21, 'iso_a3'] = 'NOR'
    world.at[43, 'iso_a3'] = 'FRA'
    world.at[160, 'iso_a3'] = 'CYP'
    world.at[167, 'iso_a3'] = 'SOM'
    world.at[174, 'iso_a3'] = 'XKX'
    return world


def plot_worldmap(count_per_country3_map, legend=False, name="Undefined", cmap='Greens', missing_kwds=None):
    if missing_kwds is None:
        missing_kwds = {'color': 'lightgrey'}
    if 'color' not in missing_kwds.keys():
        missing_kwds['color'] = 'lightgrey'

    world = get_geopandas_world()

    world[name] = world['iso_a3'].apply(
        lambda x: count_per_country3_map[x] if x in count_per_country3_map else None)

    if legend:
        fig, ax = plt.subplots(1, 1)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        w_plt = world.plot(column=name, cmap=cmap, ax=ax, legend=True, cax=cax, missing_kwds=missing_kwds)
    else:
        w_plt = world.plot(column=name, cmap=cmap, missing_kwds=missing_kwds)

    return w_plt


def _is_exclusive(series):
    vcs = series.value_counts()
    return True in vcs.index and vcs[True] == 1


def create_plot_from_truth_matrix(df, style='bar', names=None, with_exclusives=False):
    if with_exclusives:
        exclusive = df[df.apply(_is_exclusive, axis=1)]

    df_count = df.apply(pd.value_counts)
    if with_exclusives:
        ex_count = exclusive.apply(pd.value_counts)

    # names can either be None, a dict with substitutions for column names or
    # a iterable with replacements for the current column names in the same order
    if names:
        if type(names) is not dict:
            names = dict(zip(df_count.columns, names))
        df_count = df_count.rename(columns=names)
        if with_exclusives:
            ex_count = ex_count.rename(columns=names)

    ret = df_count.loc[True].plot(kind=style, color='lightgrey')
    ret = df_count.loc[True].plot(kind=style, fill=(not with_exclusives))
    if with_exclusives and True in ex_count.index:
        ret = ex_count.loc[True].plot(kind=style)

    return ret
