# %%

import pandas as pd
import numpy as np
import seaborn as sns
from unipark import Preprocessor
from unipark import MetadataManipulator as MdManipulator
from unipark import CodeBookPageManipulator as CbpManipulator
from unipark import CodeBookParser
from unipark.utils.frame import get_finishers, get_pausers, get_nonstarters
from unipark.utils.plot import plot_worldmap, create_plot_from_truth_matrix, plot_wordcloud
import matplotlib.pyplot as plt
from functools import reduce
import json
import os
from wordcloud import WordCloud, STOPWORDS

# %%

codebook_path = '../test2/codebook.csv'
input_csv = '../test2/data.csv'
figures_save_dir = '../test2/figs/auto_gen'


# %%

def page_id_unifyer(x):
    tl = {  # page map
        4584574: 10,
        4584575: 20,
        4584576: 30,
        4584577: 40,
        4584578: 41,
        4584579: 45,
        4584580: 50,
        4584581: 60,
        4584582: 70,
        4342262: 10,
        4342263: 20,
        4342264: 30,
        4342265: 40,
        4342266: 41,
        4342267: 45,
        4342268: 50,
        4342269: 60,
        4342270: 70,
        4343844: 10,
        4343845: 20,
        4343846: 30,
        4343847: 40,
        4343848: 41,
        4343849: 45,
        4343850: 50,
        4343851: 60,
        4343852: 70,
    }
    if int(x) in tl:
        x = str(tl[int(x)])
    return x


# cbp = CodeBookParser(codebook_path ,reassign_page_id=page_id_unifyer)
cbp = CodeBookParser(codebook_path)
codebook = cbp.get_codebook()
page_name_by_id = {}
for page in codebook['pages']:
    page_name_by_id[page['id']] = page['title']


def to_named_page(x):
    return page_name_by_id[str(x)] if str(x) in page_name_by_id else str(x)


# %%


# %%

pproc = Preprocessor(pd.read_csv(input_csv, sep=";"), to_named_page)
pproc.drop_nonstarters()
#pproc.apply_manipulator(MdManipulator())
for pagebook in cbp.get_codebook()['pages']:
    pproc.apply_manipulator(CbpManipulator(pagebook))

# %%

codebook

# %%

print('# {}'.format(cbp.get_codebook()['title']))
for page in pproc.pages:
    if (len(pproc.question_ids_by_page[page]) > 0):
        print('## {}'.format(page))


# %%

def question_to_markdown(question_id, headline_format='### {}', directory='./figs'):
    ret = headline_format.format(pproc.get_question_title(question_id)) + '\n'

    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, question_id)

    style = pproc.style_by_question_id[question_id]
    columns = pproc.columns_by_question_id[question_id]
    question = pproc.get_question_title(question_id)
    my_data = pproc.get_data()
    if 'single' == style:
        ret += default_eval_single_question(my_data, question_id=question_id, file_prefix=path)
    elif 'multiple' == style:
        ret += default_eval_multiple_question(my_data, columns=columns, file_prefix=path)
    elif 'rank' == style:
        print(f'{style} not supported yet!')
    elif 'free' == style:
        ret += default_eval_free_question(my_data, question_id=question_id, file_prefix=path)
    elif 'matrix' == style:
        ret += default_eval_matrix(my_data, columns=columns, file_prefix=path)
        print(f'{style} not supported yet!')
    else:
        assert False, 'Unknown stlye "{}"'.format(style)

    return ret


# %%

def page_to_markdown(page, headline_format='## {}', directory='./figs'):
    ret = headline_format.format(page) + '\n'
    question_ids = pproc.question_ids_by_page[page]
    path = os.path.join(directory, page.replace(' ', '_').replace('?', ''))

    if not question_ids:
        ret = ret[:-1] + ': Empty\n'
        return ret

    for question_id in question_ids:
        ret += question_to_markdown(question_id, directory=path)
    return ret


# %%


# %%

def default_eval_single_question(data: pd.DataFrame, question_id, file_prefix=None, show=False):
    columns = pproc.columns_by_question_id[question_id]
    vcs = data[columns[0]].value_counts()
    count = reduce((lambda a, b: a + b), vcs.apply(lambda x: int(x) if x else 0), 0)
    if count == 0:
        return 'Nobody answered this question!'
    ret = 'This question was answered by {} participants. The votes were distributed according to the following graphs:\n'.format(
        count)
    if len(vcs) <= 10:
        # Pie chart
        vcs.plot.pie()
        if file_prefix is not None:
            path = file_prefix + '_all_sorted_pie.png'
            ret += '![alt text]({} "Title")\n'.format(path)
            plt.savefig(path, dpi=1200, bbox_inches='tight')
        if show:
            _ = plt.show()
        else:
            plt.clf()

    # Bar chart
    vcs.plot.bar()
    if file_prefix is not None:
        path = file_prefix + '_all_sorted_bar.png'
        ret += '![alt text]({} "Title")\n'.format(path)
        plt.savefig(path, dpi=1200, bbox_inches='tight')
    if show:
        _ = plt.show()
    else:
        plt.clf()

    # Finishers only
    data = get_finishers(data)
    vcs = data[columns[0]].value_counts()
    count = reduce((lambda a, b: a + b), vcs.apply(lambda x: int(x) if x else 0))
    ret += 'Looking at the votes of the {} finishers only, we receive the following distribution:\n'.format(count)

    if len(vcs) <= 10:
        # Pie chart
        vcs.plot.pie()
        if file_prefix is not None:
            path = file_prefix + '_finishers_sorted_pie.png'
            ret += '![alt text]({} "Title")\n'.format(path)
            plt.savefig(path, dpi=1200, bbox_inches='tight')
        if show:
            _ = plt.show()
        else:
            plt.clf()

    # Bar chart
    vcs.plot.bar()
    if file_prefix is not None:
        path = file_prefix + '_finishers_sorted_bar.png'
        ret += '![alt text]({} "Title")\n'.format(path)
        plt.savefig(path, dpi=1200, bbox_inches='tight')
    if show:
        _ = plt.show()
    else:
        plt.clf()

    # same but retain order
    order = pproc.order_of_question_id[question_id]
    vcs_ordered = get_ordered_value_counts(vcs, order)

    if len(vcs_ordered) <= 10:
        # Pie chart
        vcs_ordered.plot.pie()
        if file_prefix is not None:
            path = file_prefix + '_all_ordered_pie.png'
            ret += '![alt text]({} "Title")\n'.format(path)
            plt.savefig(path, dpi=1200, bbox_inches='tight')
        if show:
            _ = plt.show()
        else:
            plt.clf()

    # Bar chart
    vcs_ordered.plot.bar()
    if file_prefix is not None:
        path = file_prefix + '_all_ordered_bar.png'
        ret += '![alt text]({} "Title")\n'.format(path)
        plt.savefig(path, dpi=1200, bbox_inches='tight')
    if show:
        _ = plt.show()
    else:
        plt.clf()

    # Finishers only
    data = get_finishers(data)
    vcs = data[columns[0]].value_counts()
    vcs_ordered = get_ordered_value_counts(vcs, order)
    count = reduce((lambda a, b: a + b), vcs.apply(lambda x: int(x) if x else 0))
    ret += 'Looking at the votes of the {} finishers only, we receive the following distribution:\n'.format(count)

    if len(vcs_ordered) <= 10:
        # Pie chart
        vcs_ordered.plot.pie()
        if file_prefix is not None:
            path = file_prefix + '_finishers_ordered_pie.png'
            ret += '![alt text]({} "Title")\n'.format(path)
            plt.savefig(path, dpi=1200, bbox_inches='tight')
        if show:
            _ = plt.show()
        else:
            plt.clf()

    # Bar chart
    vcs_ordered.plot.bar()
    if file_prefix is not None:
        path = file_prefix + '_finishers_ordered_bar.png'
        ret += '![alt text]({} "Title")\n'.format(path)
        plt.savefig(path, dpi=1200, bbox_inches='tight')
    if show:
        _ = plt.show()
    else:
        plt.clf()

    # ToDo: Bar finisher over all

    return ret


# %%

def get_ordered_value_counts(value_counts, order):
    vcs_ordered = value_counts.copy()
    for i in order:
        if i not in vcs_ordered.index:
            vcs_ordered[i] = 0
    forwards = dict(zip(order, np.arange(len(order))))
    backwards = dict(zip(np.arange(len(order)), order))
    vcs_ordered = vcs_ordered.rename(index=forwards).sort_index().rename(index=backwards)
    return vcs_ordered


# %%

def default_eval_multiple_question(data, columns, file_prefix=None, show=False):
    ret = ''
    bool_columns = [x for x in columns if data[x].dtype == bool]
    labels = [x[8:] for x in bool_columns]
    create_plot_from_truth_matrix(data[bool_columns], names=labels, with_exclusives=True)
    if file_prefix is not None:
        path = file_prefix + '_distribution_bar.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show:
        _ = plt.show()
    else:
        plt.clf()

    # ticks = data[bool_columns].apply(np.count_nonzero, axis=1)
    # sns.violinplot(x=ticks, cut=0)
    # if file_prefix is not None:
    #    path = file_prefix + '_vote-count_distribution_violin.png'
    #    plt.savefig(path, dpi=1200, bbox_inches='tight')
    #    ret += '![alt text]({} "Title")\n'.format(path)
    # if show: _=plt.show()
    # else: plt.clf()

    ticks = data[bool_columns].apply(np.count_nonzero, axis=1)
    sns.histplot(x=ticks, discrete=True)
    if file_prefix is not None:
        path = file_prefix + '_vote-count_distribution_hist.png'
        plt.savefig(path, dpi=1200, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)
    if show:
        _ = plt.show()
    else:
        plt.clf()

    non_bool_columns = [x for x in columns if x not in bool_columns]
    for column in non_bool_columns:
        path = file_prefix + '_' + column.replace(' ', '_').replace('?', '') + '_wordcloud.png' if file_prefix else None
        p = plot_wordcloud(data[column], save_file=path)
        if path and p is not None:
            ret += 'Of those ({}) who filled out "{}" the following wordcloud could be built:\n'.format(
                np.count_nonzero(data[column].apply(lambda x: x is not None)),
                column)
            ret += '![alt text]({} "Title")\n'.format(path)

    return ret


# %%

def default_eval_matrix(data: pd.DataFrame, columns, file_prefix=None, show=False):
    sd = data[columns[0]]
    vcs = []
    for col in sd.columns:
        col_data = sd[col]
        col_vc = col_data.value_counts()
        col_vc = col_vc.rename('count')
        col_vc = col_vc.to_frame()
        col_vc['answer'] = col_vc.index
        col_vc['col'] = col
        col_vc = col_vc.reset_index(drop=True)
        vcs.append(col_vc)
    counts = pd.concat(vcs)
    sns.barplot(data=counts, x='col', y='count', hue='answer')
    #counts = pd.concat(vcs, axis=1).fillna(0).astype(int)
    print(columns)
    # q, a , c
    return ''


# %%

def combine_strs(a, b):
    a = '' if a is None or (type(a) == float and np.isnan(a)) else str(a)
    b = '' if b is None or (type(b) == float and np.isnan(b)) else str(b)
    return a + ' ' + b


# %%

def default_eval_free_question(data, question_id, file_prefix=None, show=False):
    series = data[pproc.columns_by_question_id[question_id][0]]
    ret = 'A total of {} participants answered this question.\n'.format(
        np.count_nonzero(series.apply(lambda x: x is not None)))
    text = reduce(combine_strs, series)

    if text.strip():
        # Generate word cloud
        wordcloud = WordCloud(width=3000, height=1000, random_state=1, background_color='white', collocations=False,
                              stopwords=STOPWORDS).generate(text)

        plt.figure(figsize=(40, 30))

        # Display image
        plt.imshow(wordcloud)
        # No axis details
        plt.axis("off");

        if file_prefix:
            ret += 'The answers result in the following wordcloud:\n'
            path = file_prefix + "_wordcloud.png"
            plt.savefig(path, bbox_inches='tight')
            ret += '![alt text]({} "Title")\n'.format(path)

        if not show:
            plt.cla()
            plt.clf()
            plt.close()

    return ret


# %%

report = '# {}\n'.format(cbp.get_codebook()['title'])
print('# {}'.format(cbp.get_codebook()['title']))
for page in pproc.pages[-2:]:
    mpage = page_to_markdown(page, directory=figures_save_dir)
    print(mpage)
    report += mpage

# %%

#with open('data/Report.md', 'w+') as file:
#    file.write(report)

# %%


# %%


