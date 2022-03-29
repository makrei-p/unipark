import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def _is_exclusive(series):
    vcs = series.value_counts()
    return True in vcs.index and vcs[True] == 1


def histogram(df, style='bar', names=None, with_exclusives=False, order=None, file_prefix=None, show=False):
    if with_exclusives:
        exclusive = df[df.apply(_is_exclusive, axis=1)]

    df_count = df.apply(pd.value_counts)
    if with_exclusives:
        ex_count = exclusive.apply(pd.value_counts)

    # names can either be None, a dict with substitutions for column names or  a iterable with replacements for the current column names in the same order
    if names:
        if type(names) is not dict:
            names = dict(zip(df_count.columns, names))
        df_count = df_count.rename(columns=names)
        if with_exclusives:
            ex_count = ex_count.rename(columns=names)
    
    # reorder columns
    if order:
        if order == 'count':
            new_columns = df_count.columns[df_count.loc[0].argsort()]
            df_count = df_count[new_columns]
        elif order == 'alphabetic': 
            df_count = df_count.reindex(sorted(df_count.columns), axis=1)

    result = df_count.loc[True].plot(kind=style, color='lightgrey')
    result = df_count.loc[True].plot(kind=style, fill=(not with_exclusives))
    if with_exclusives and True in ex_count.index:
        result = ex_count.loc[True].plot(kind=style)

    ret = ''
    if file_prefix is not None:
        path = file_prefix + '_distribution_' + style + '.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show: _=plt.show()
    else: plt.clf()

    return ret

def vote_count(ticks, file_prefix=None, show=False):
    ret = ''

    sns.histplot(x=ticks, discrete=True)
    if file_prefix is not None:
        path = file_prefix + '_vote-count_distribution_hist.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show: _=plt.show()
    else: plt.clf()

    return ret