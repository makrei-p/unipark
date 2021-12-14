import datetime

from unipark.preprocessing.manipulator_blueprint import Manipulator


def date_str_to_datetime(x):
    return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")


def guess_platform_from_browser(it):
    if "Windows" in it:
        return "Windows"
    elif "Macintosh" in it:
        return "Macintosh"
    elif "Android" in it:
        return "Android"
    elif "Linux" in it:
        return "Linux"
    elif "iPhone" in it:
        return "iPhone"
    else:
        return "Unknown"


disp_translator = {
    10: "consent seen",
    11: "not invited yet",
    12: "invited",
    16: "reserved 1",
    17: "reserved 2",
    13: "inactive",
    14: "email undeliverable",
    15: "unavailable",
    18: "custom unavailable 1",
    19: "custom unavailable 2",
    20: "not begun yet",
    21: "answering now",
    22: "paused",
    23: "continued",
    31: "finished",
    32: "finished after pause",
    33: "custom finished 1",
    34: "custom finished 2",
    35: "denied at login (quota exceeded)",
    36: "denied (quota exceeded)",
    37: "screened out",
    38: "custom screened out 1",
    39: "custom screened out 2",
    40: "custom screened out 3",
    41: "quote closed",
    42: "consent denied",
    43: "personal data deleted"
}


class MetadataManipulator(Manipulator):
    page_id = 0

    def transform_data(self, data):
        data['platform'] = data['browser'].apply(guess_platform_from_browser)

        data['dispcode_named'] = data['dispcode'].apply(lambda x: disp_translator[x])

        # make dates usable (convert to datetime)
        data['date_of_last_access'] = data['date_of_last_access'].apply(date_str_to_datetime)
        data['date_of_start'] = data['datetime'].apply(date_str_to_datetime)

        # make page_history usable (make it a list of pages or None if empty)
        data['page_history'] = data['page_history'].apply(lambda x: [int(y) for y in x.split(',')] if x else None)
        return data

    def get_page_id(self):
        return self.page_id

    def get_inferred_columns(self):
        return ['platform', 'dispcode_named', 'date_of_start']

    def get_questions(self):
        return []  # Metadata has no questions!

    def get_columns_of_question(self, question):
        return []

    def get_question_style(self, question):
        """
        :param question: string as in get_questions identifying a question
        :return: 'single' (single choice), 'multiple' (multiple choice), 'free' (free text) or 'rate' (rating).
                 None if it isn't a question
        """
        return None

    def get_value_order_for_question(self, question):
        return []

    def get_protected_columns(self):
        return []

    def get_removable_columns(self):
        return ['datetime']

    def get_metadata_columns(self):
        return ['platform', 'dispcode_named', 'date_of_start']
