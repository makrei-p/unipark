import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

from . import likert


def barplot(data:pd.DataFrame, columns, file_prefix=None, show=False):
    ret = ''

    # count the values
    vcs = []
    for col in columns[0]:
        col_data = data[col]
        col_vc = col_data.value_counts()
        col_vc = col_vc.rename('count')
        col_vc = col_vc.to_frame()
        col_vc['answer'] = col_vc.index
        col_vc['col'] = col
        col_vc = col_vc.reset_index(drop=True)
        vcs.append(col_vc)
    counts = pd.concat(vcs)

    counts['col'] = list(map(lambda name: clean_columname(name), counts['col']))

    # plot the distribution of answers for each question
    sns.barplot(data=counts, x='col', y='count', hue='answer')
    plt.xticks(rotation=45, horizontalalignment='right')
    plt.tight_layout()
    if file_prefix is not None:
        path = file_prefix + '_matrix_bar_q.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show: _=plt.show()
    else: plt.clf()

    # plot the overall distribution of questions for each answer
    sns.barplot(data=counts, hue='col', y='count', x='answer')
    plt.xticks(rotation=45, horizontalalignment='right')
    plt.tight_layout()
    if file_prefix is not None:
        path = file_prefix + '_matrix_bar_a.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show: _=plt.show()
    else: plt.clf()    

    return ret


def likertmatrix(data, columns, file_prefix=None, show=False):
    ret = ''

    # parse the data into a table
    scale = None
    responses = {}
    for col in columns[0]:
        # get the data of the current column 
        col_data = data[col]

        # parse the data into a tabular format
        col_vc = col_data.value_counts()

        # determine the most likely likert scale
        if scale == None:
            scale = likert.determine_scale(col_vc.index)
        responses[clean_columname(col)] = list(map(lambda s: col_vc[s] if (s in col_vc.index) else 0, scale))


    # calculate the buffer such that all bars are aligned on their middle
    halfway = list(map(lambda r: responses[r][0]+responses[r][1]+(responses[r][2]/2.0), responses))
    buffer = list(map(lambda h: max(halfway)-h, halfway))
    for i, key in enumerate(responses.keys()):
        responses[key] = [buffer[i]] + responses[key]
    scale = ['buffer'] + scale

    # create the matrix
    labels = list(responses.keys())
    data = np.array(list(responses.values()))
    data_cum = data.cumsum(axis=1)

    # draw the likert colors from a colormap
    category_colors = likert.cmap(np.linspace(0.15, 0.85, data.shape[1]-1))

    _, ax = plt.subplots(figsize=(8, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    plt.axvline(x=max(halfway), c='grey', linestyle='--', alpha=0.5)

    # iterate over all options of the scale and associate it with an index and color
    for i, (colname, color) in enumerate(zip(scale[1:], category_colors)):
        widths = data[:, i+1]
        starts = data_cum[:, i+1] - widths# + buffer
        rects = ax.barh(labels, widths, left=starts, height=0.5, label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        # ax.bar_label requires matplotlib version 3.4
        ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncol=len(scale), bbox_to_anchor=(-0.3, 1), loc='lower left', fontsize='small')

    # save the figure
    if file_prefix is not None:
        path = file_prefix + '_matrix_likert.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show: _=plt.show()
    else: plt.clf()    
    return ret   

# extract the actual columname from the Unipark-columnames
def clean_columname(coltext):
    colname = re.search('v_[0-9]+ \((.+?)\)', coltext)
    if colname:
        colname = colname.group(1).strip()
    else:
        #print('ERROR: no string matched the regex in "' + str(coltext) + '"')
        colname = re.search('\((.+?)\)', coltext)
        if colname:
            colname = colname.group(1).strip()

    # special case: if a columname contains brackets (and ends with closing brackets), then these are cut off
    if '(' in colname and ')' not in colname:
        colname = colname+')'

    print(f'{coltext} -> {colname}')
    return colname