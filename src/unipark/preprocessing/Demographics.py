import json

from unipark.utils.frame import to_named_pages, translate_multiple_choice, translate_single_choice, translate_free_text

from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2, \
    country_name_to_country_alpha3

page_id = 10


def get_continent(col):
    try:
        cn_continent = country_alpha2_to_continent_code(col)
    except:
        cn_continent = 'Unknown'
    return cn_continent


def get_cn_a2(col):
    try:
        cn_a2_code = country_name_to_country_alpha2(col)
    except:
        if col == "Antigua & Barbuda":
            cn_a2_code = "AG"
        else:
            cn_a2_code = 'Unknown'
    return cn_a2_code


def get_cn_a3(col):
    try:
        cn_a3_code = country_name_to_country_alpha3(col)
    except:
        if col == "Antigua & Barbuda":
            cn_a3_code = "ATG"
        else:
            cn_a3_code = 'Unknown'
    return cn_a3_code


class Manipulator:

    def __init__(self):
        with open('codebook/1_demographics/v_1.json') as file:
            self.codebook_v_1 = json.load(file)
        with open("codebook/1_demographics/job_roles_map.json") as file:
            self.job_translator = json.load(file)
        with open("codebook/1_demographics/years_experience_map_v19.json") as file:
            self.years_exp_map = json.load(file)
        with open("codebook/1_demographics/projectsize_map_v21.json") as file:
            self.size_map = json.load(file)
        with open("codebook/1_demographics/industry_map.json") as file:
            self.industry_map = json.load(file)

        self.inferred_columns = []
        self.protected_columns = []
        self.removable_columns = []
        self.questions = []
        self.q2c_map = {}
        self.q2s_map = {}
        self.q2o_map = {}  # map original value-order for question
        self.q2i_map = {}  # map id for question


    def transform_data(self, data):
        # q1
        question = 'In which country are you working?'

        data['CountryName'] = data['v_1'].apply(
            lambda x: self.codebook_v_1[str(x)] if str(x) in self.codebook_v_1.keys() else None)
        data['Country'] = data['CountryName'].apply(lambda x: get_cn_a2(x))
        data['Country3'] = data['CountryName'].apply(lambda x: get_cn_a3(x))
        data['Continent'] = data['Country'].apply(lambda x: get_continent(x))

        columns = ['CountryName', 'Country', 'Country3', 'Continent']
        self.inferred_columns += columns
        self.removable_columns += ['v_1']
        self.q2c_map[question] = ['CountryName']
        self.q2s_map[question] = 'single'
        self.q2i_map[question] = 9876541
        self.questions += [question]

        # q2
        question = 'Which job functions did you have in the last five years?'
        roles, varchars = translate_multiple_choice(data, self.job_translator, 'job')
        self.inferred_columns += roles
        self.inferred_columns += varchars
        self.protected_columns += varchars
        self.removable_columns += list(self.job_translator.keys())
        self.q2c_map[question] = roles + varchars
        self.q2s_map[question] = 'multiple'
        self.q2i_map[question] = 9876542
        self.questions += [question]

        # q3
        question = 'How many years of experience do you have in software engineering?'
        data['Years experience'] = data['v_19'].apply(lambda x: self.years_exp_map[str(x)] if x != 0 else None)
        self.inferred_columns += ['Years experience']
        self.removable_columns += ['v_19']
        self.q2c_map[question] = ['Years experience']
        self.q2s_map[question] = 'single'
        self.q2i_map[question] = 9876543
        self.questions += [question]

        # q4
        question = 'Which software development paradigm do you follow?'
        dp_map = {'int': 'Development paradigm',
                  '1': 'Rather agile',
                  '2': 'Rather plan-driven',
                  '3': 'Rather hybrid'}
        target = translate_single_choice(data, dp_map, 'v_16')
        self.inferred_columns += [target]
        self.removable_columns += ['v_16']
        self.q2c_map[question] = [target]
        self.q2s_map[question] = 'single'
        self.q2i_map[question] = 9876544
        self.questions += [question]

        # q5
        question = 'Which software process model do you use (optional)'
        target = translate_free_text(data, 'v_198', 'Software process model')
        self.inferred_columns += [target]
        self.removable_columns += ['v_198']
        self.protected_columns += [target]
        self.q2c_map[question] = [target]
        self.q2s_map[question] = 'free'
        self.q2i_map[question] = 9876545
        self.questions += [question]

        # q6
        question = 'How many people are involved in your current project?'
        target = translate_single_choice(data, self.size_map, 'v_21')
        self.inferred_columns += [target]
        self.removable_columns += ['v_21']
        self.q2c_map[question] = [target]
        self.q2s_map[question] = 'single'
        self.q2i_map[question] = 9876546
        self.questions += [question]

        # q7
        question = 'What industry is your current project for?'
        translator = self.industry_map
        roles, varchars = translate_multiple_choice(data, translator, 'job')
        self.inferred_columns += roles
        self.inferred_columns += varchars
        self.protected_columns += varchars
        self.removable_columns += list(translator.keys())
        self.q2c_map[question] = roles + varchars
        self.q2s_map[question] = 'multiple'
        self.q2i_map[question] = 98765417
        self.questions += [question]

        # q8
        question = '''What is your project's main programming language?'''
        translator = self.language_map
        roles, varchars = translate_multiple_choice(data, translator, 'job')
        self.inferred_columns += roles
        self.inferred_columns += varchars
        self.protected_columns += varchars
        self.removable_columns += list(translator.keys())
        self.q2c_map[question] = roles + varchars
        self.q2s_map[question] = 'multiple'
        self.q2i_map[question] = 9876548
        self.questions += [question]

        return data


    def get_page_id(self):
        return 10

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
        return self.q2s_map.get(question, None)

    def get_value_order_for_question(self, question):
        return []

    def get_protected_columns(self):
        return self.protected_columns

    def get_removable_columns(self):
        return self.removable_columns

    def get_metadata_columns(self):
        return []

    def get_question_id(self, question):
        return self.q2i_map.get(question)
