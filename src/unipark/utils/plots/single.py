import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from os.path import exists

from . import likert

# generate a bar chart for a single choice question
def barchart(data: pd.Series, use_likert: bool=False, file_prefix=None, show=False):
    # generate a bar chart
    _, ax = plt.subplots()

    # check if the scale is actually a likert scale
    if not likert.determine_scale(list(data.index)):
        use_likert = False
    # if the question is supposed to be on a likert scale, use the likert colors
    pltcolor = None
    if use_likert:
        pltcolor = likert.cmap(np.linspace(0.15, 0.85, len(data.index)))
    barc = plt.bar(x=list(range(0, len(data.index))), height=list(data.values), width=0.8, color=pltcolor, tick_label=list(data.index))
    ax.bar_label(barc, label_type='edge')
    plt.xticks(rotation=30)

    # generate the alternative text, generate the plot and return the markdown line
    alttext = [f'{d}: {data[d]}' for d in data.keys()]
    ret = saveplt(file_prefix=f'{file_prefix}_bar', alttext=alttext)
    return ret

# generate a pie chart for a single choice question
def piechart(data: pd.Series, use_likert: bool=False, file_prefix=None, show=False):
    _, ax = plt.subplots()

    # check if the scale is actually a likert scale
    if not likert.determine_scale(list(data.index)):
        use_likert = False
    # if the question is supposed to be on a likert scale, use the likert colors
    pltcolor = None
    if use_likert:
        pltcolor = likert.cmap(np.linspace(0.15, 0.85, len(data.index)))
    ax.pie(x=list(data.values), labels=list(data.index), colors=pltcolor)

    # generate the alternative text, generate the plot and return the markdown line
    alttext = [f'{d}: {data[d]}' for d in data.keys()]
    ret = saveplt(file_prefix=f'{file_prefix}_pie', alttext=alttext)
    return ret

# save the current plot and create a markdown line with an alternate text
def saveplt(file_prefix: str, alttext: str='alttext', show=False):
    index = 0
    while exists(f'{file_prefix}_{index}.png'):
        index += 1

    path = f'{file_prefix}_{index}.png'
    ret = f'![{alttext}]({path} "Title")\n'
    plt.savefig(path, dpi=1200, bbox_inches='tight')

    # display the plot if the show option is set, otherwise reset the plot
    if show: _=plt.show()
    else: plt.clf()

    return ret