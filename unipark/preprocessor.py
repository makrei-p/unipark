import pandas as pd
import datetime
from functools import reduce
from unipark.preprocessing.manipulator_blueprint import Manipulator
from unipark.utils.frame import get_nonstarters


def get_cleaned_frame(csv):  # Unused?!
    return pd.read_csv(csv)


def date_str_to_datetime(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")


def rename_pages(df, page_map):
    df = df.rename(columns=dict(
        zip(["rts" + str(x) for x in page_map.keys()], ["rts" + str(page_map[x]) for x in page_map.keys()])))

    df['lastpage'] = df['lastpage'].apply(lambda x: page_map[x] if x in page_map.keys() else x)

    def replace_page_history(x):
        if type(x) == str:  # data is in its original form "page_id,page_id,..."
            pages = x.split(',')
            pages = [page_map[int(page)] if page and page != '0' else page for page in pages]
            return reduce((lambda a, b: str(a) + ',' + str(b)), pages)

        else:  # prepare metadata was called and it is a list
            return [page_map[page] if page in page_map.keys() else page for page in x]

    df['page_history'] = df['page_history'].apply(replace_page_history)

    return df


# list of columns to be dropped when preparing metadata
drop_list = [
    'date_of_first_mail',
    'tester',
    'quality',
    'quota_assignment',
    'quota',
    'javascript',
    'flash',
    'output_mode',
    'language',
    'cleaned',
    'external_lfdn',
    'device_type',
    'ats',
    'hflip', 'vflip',
    'session_id',
]


class Preprocessor:

    def __init__(self, data: pd.DataFrame, to_named_page = lambda x: str(x)):
        """
        Preprocesses the given data frame for further analysis and creates the preprocessor object.
        :param data:
        """
        self.inferred_columns = []
        self.pages = []
        self.page_ids = []
        self.question_ids_by_page = {}
        self.columns_by_question_id = {}
        self.style_by_question_id = {}
        self.order_of_question_id = {}
        self.title_of_question_id = {}
        self.protected_columns = []  # Columns which may contain personal data, e.g. varchar columns
        self.removable_columns = [x for x in drop_list if x in data.columns]

        # all vars start with 'v_'. There are no custom columns yet so the remaining ones are metadata
        self.metadata_columns = [x for x in data.columns if not x.startswith('v_')]

        self.data = data
        self.to_named_page = to_named_page

    def get_data(self):
        return self.data

    def get_metadata(self):
        return self.data[self.metadata_columns]

    def rename_pages(self, page_map):
        """
        Renames the pages in this self.data's Dataframe using the function @Preprocessor.rename_pages using the given
        page_map.
        Renaming pages is NOT done in the constructor / while initializing the Preprocessor and has to be invoked
        manually if desired!
        :param page_map: dict mapping current_page_name -> new_page_name; page_names not provided in the dict will
        remain unchanged.
        :return: None; changes values internally!
        """
        self.data = rename_pages(self.data, page_map)

    def apply_manipulator(self, manipulator:Manipulator):
        new_data = manipulator.transform_data(self.data.copy())

        cols = manipulator.get_inferred_columns()
        for x in cols:
            if x in self.inferred_columns:
                print(manipulator)
                print(cols)
                print()
                print(self.inferred_columns)
                assert False, 'Redundant inferred column "{}"'.format(x)

        self.data = new_data
        self.inferred_columns += cols
        self.removable_columns += manipulator.get_removable_columns()
        self.protected_columns += manipulator.get_protected_columns()
        self.metadata_columns += manipulator.get_metadata_columns()

        page_id = manipulator.get_page_id()
        if page_id > 0:
            page = self.to_named_page(page_id)
            self.pages += [page]
            self.page_ids += [page_id]


            questions = manipulator.get_questions()
            self.question_ids_by_page[page] = [manipulator.get_question_id(q) for q in questions]

            for q in questions:
                id = manipulator.get_question_id(q)
                self.columns_by_question_id[id] = manipulator.get_columns_of_question(q)
                self.style_by_question_id[id] = manipulator.get_question_style(q)
                self.order_of_question_id[id] = manipulator.get_value_order_for_question(q)
                self.title_of_question_id[id] = q

        return True

    def apply_codebook(self, codebook):
        return False

    def drop_removable(self):
        self.data = self.data.drop(columns=self.removable_columns)

        #remove occurences in other lists:
        self.metadata_columns = [x for x in self.metadata_columns if x not in self.removable_columns]
        self.inferred_columns = [x for x in self.inferred_columns if x not in self.removable_columns]
        self.protected_columns = [x for x in self.protected_columns if x not in self.removable_columns]

        # all done, clear removables
        self.removable_columns = []

    def drop_nonstarters(self):
        self.data = self.data.drop(index=get_nonstarters(self.data).index)

    def get_page_id(self, page):
        return self.page_ids[self.pages.index(page)]

    def get_question_title(self, id):
        return self.title_of_question_id[id]
