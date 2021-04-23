from abc import ABC

import pandas as pd


class Manipulator(ABC):
    def transform_data(self, data: pd.DataFrame):
        return data

    def get_page_id(self):
        '''

        :return: Negative value for no_page, 0 for metadata, >0 for page_id
        '''
        return -1

    def get_inferred_columns(self):
        '''

        :return: List of column names added by transform_data
        '''
        return []

    def get_questions(self):
        return []

    def get_columns_of_question(self, question):
        return []

    def get_question_style(self, question):
        '''
        :param question: string as in get_questions identifying a question
        :return: 'single' (single choice), 'multiple' (multiple choice), 'free' (free text) or 'rank' (ranking). None if it isn't a question
        '''
        return None

    def get_value_order_for_question(self, question):
        return []

    def get_question_id(self, question):
        return None

    def get_protected_columns(self):
        return []

    def get_removable_columns(self):
        return []

    def get_metadata_columns(self):
        return []
