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
########
codebook_path = '../test2/codebook.csv'
input_csv = '../test2/data.csv'
figures_save_dir = '../test2/figs/auto_gen'
########
cbp = CodeBookParser(codebook_path)
codebook = cbp.get_codebook()
page_name_by_id = {}
for page in codebook['pages']:
    page_name_by_id[page['id']] = page['title']


def to_named_page(x):
    return page_name_by_id[str(x)] if str(x) in page_name_by_id else str(x)

########
pproc = Preprocessor(pd.read_csv(input_csv,sep=";"), to_named_page)
pproc.drop_nonstarters()
pproc.apply_manipulator(MdManipulator())
for pagebook in cbp.get_codebook()['pages']:
    pproc.apply_manipulator(CbpManipulator(pagebook))