import geopandas
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def get_geopandas_world():
    world = geopandas.read_file(
        geopandas.datasets.get_path('naturalearth_lowres'))
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
        w_plt = world.plot(column=name, cmap=cmap, ax=ax,
                           legend=True, cax=cax, missing_kwds=missing_kwds)
    else:
        w_plt = world.plot(column=name, cmap=cmap, missing_kwds=missing_kwds)

    return w_plt
