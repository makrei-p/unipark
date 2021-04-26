import re

from unipark.utils.frame import translate_multiple_choice, translate_single_choice, translate_free_text
from unipark.preprocessing.manipulator_blueprint import Manipulator


class CodeBookPageManipulator(Manipulator):

    def __init__(self, pagebook):
        self.pagebook = pagebook
        self.inferred_columns = []
        self.protected_columns = []
        self.removable_columns = []
        self.questions = []
        self.q2c_map = {} # map columns for question
        self.q2s_map = {} # map style for question
        self.q2o_map = {} # map original value-order for question
        self.q2i_map = {} # map id for question

    def transform_data(self, data):
        for question_map in self.pagebook['questions']:
            question = question_map['title']
            prefix = str(question_map['id']) + " "
            style = question_map['style']
            if style == 'single':
                new_column = translate_single_choice(data, question_map, prefix=prefix)
                order = [question_map[x] for x in question_map.keys() if type(x)== int or re.findall(r'^[0-9]+$',x)]
                self.inferred_columns.append(new_column)
                self.removable_columns.append(question_map['column'])
                self.q2c_map[question] = [new_column]
                self.q2s_map[question] = 'single'
                self.q2o_map[question] = order
                self.q2i_map[question] = question_map['id']
                self.questions += [question]
            elif style == 'multiple':
                entities, varchars = translate_multiple_choice(data, question_map, prefix=prefix)
                self.inferred_columns += entities + varchars
                self.removable_columns += [x for x in question_map.keys() if x.startswith('v_')]
                self.protected_columns += varchars
                self.q2c_map[question] = entities + varchars
                self.q2s_map[question] = 'multiple'
                self.q2i_map[question] = question_map['id']
                self.questions += [question]
            elif style == 'free':
                target = str(question_map['id']) + ' ' + question_map['varchar'] + ' string'
                source = question_map['column']
                if source not in data.columns:
                    source = question_map['alt_column']
                data[target]= data[source].apply(lambda x: x if type(x) is str and x!='-99' and x != '-66' else None)
                self.inferred_columns.append(target)
                self.removable_columns.append(source)
                self.protected_columns.append(target)
                self.q2c_map[question] = [target]
                self.q2s_map[question] = 'free'
                self.q2i_map[question] = question_map['id']
                self.questions += [question]

            elif style == 'rank':
                entities, _ = translate_multiple_choice(data, question_map, prefix=prefix, int_converter=lambda x: int(x) if x and not str(x).startswith('-') else None)
                self.inferred_columns += entities
                self.removable_columns += [x for x in question_map.keys() if x.startswith('v_')]
                self.q2c_map[question] = entities
                self.q2s_map[question] = 'rank'
                self.q2i_map[question] = question_map['id']
                self.questions += [question]

                # print('rank is not supported yet ({})\n{}'.format(question, question_map))

            else:
                print('unknown question style: {}'.format(style))

        return data

    def get_page_id(self):
        return int(self.pagebook['id'])

    def get_inferred_columns(self):
        return self.inferred_columns.copy()

    def get_questions(self):
        return self.questions.copy()

    def get_columns_of_question(self, question):
        if question in self.q2c_map.keys():
            return self.q2c_map[question].copy()
        return None

    def get_question_style(self, question):
        '''
        :param question: string as in get_questions identifying a question
        :return: 'single' (single choice), 'multiple' (multiple choice), 'free' (free text) or 'rate' (rating). None if it isn't a question
        '''
        if question in self.q2s_map.keys():
            return self.q2s_map[question]
        return None

    def get_value_order_for_question(self, question):
        return self.q2o_map.get(question,[])

    def get_question_id(self, question):
        return self.q2i_map.get(question, -1)

    def get_protected_columns(self):
        return self.protected_columns

    def get_removable_columns(self):
        return self.removable_columns

    def get_metadata_columns(self):
        return []
