import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from wordcloud import WordCloud, STOPWORDS
from functools import reduce


def make_str(a):
    return '' if a is None or (type(a) == float and np.isnan(a)) else str(a)


def combine_strs(a, b):
    return make_str(a) + ' ' + make_str(b)

# generate a wordcloud from a series of natural language text


def wordcloud(series, file_prefix=None, show=False):
    text = reduce(combine_strs, series)

    if not text:
        return '(no text found)\n'

    # Generate word cloud
    wordcloud = WordCloud(width=3000, height=1000, random_state=1, background_color='white',
                          collocations=False, stopwords=STOPWORDS).generate(text)
    plt.figure(figsize=(40, 30))
    plt.imshow(wordcloud)

    ret = ""
    if file_prefix:
        path = file_prefix + "_wordcloud.png"
        plt.savefig(path, bbox_inches='tight')
        ret += '![alt text]({} "Title")\n'.format(path)

    # display the plot if the show option is set, otherwise reset the plot
    if show:
        _ = plt.show()
    else:
        plt.clf()

    return ret

# generate a list of natural language text


def textlist(series):
    ret = 'Verbatim Answers:\n'
    answers = [answer for answer in list(series.values) if answer is not None]
    for answer in answers:
        ret += '* ' + str(answer) + '\n'

    return ret


def multitextlist(data: pd.DataFrame, columns):
    ret = ''

    # each column represents one question
    for col in columns:
        ret += '#' + str(col) + ':\n'
        col_data = data[col]

        # each value in that column represents one answer to that question
        answers = [answer for answer in list(
            col_data.values) if answer is not None]
        for answer in answers:
            ret += '* ' + str(answer) + '\n'
        ret += '\n'
    return ret
