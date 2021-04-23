import pandas as pd


def get_finishers(df):
    '''
    Filters the DataFrame for complete replies.
    :param df:
    :return:
    '''
    return df[(df['dispcode'] >= 31) & (df['dispcode'] <= 34)]


def get_pausers(df):
    '''
    Filters the DataFrame for paused (begun but did not finish) replies.
    :param df:
    :return:
    '''
    return df[df['dispcode'] == 22]


def get_nonstarters(df):
    '''
    Filters the DataFrame for completely empty replies (not begun yet)
    :param df:
    :return:
    '''
    return df[df['dispcode'] == 20]


def filter_bool_columns(columns, data):
    return [x for x in columns if data[x].dtype == bool]


def translate_multiple_choice(df, translator_map, prefix, int_converter = lambda x: x is not 0):
    prefix += ' '
    entities = []
    varchars = []
    for var in [x for x in translator_map.keys() if x.startswith('v_')]:
        dtype, role = translator_map[var]
        role = prefix + role
        if dtype == 'int':
            df[role] = df[var].apply(int_converter)
            entities.append(role)
        if dtype == 'varchar':
            role += " string"
            df[role] = df[var].apply(lambda x: x if x != '-99' else None)
            varchars.append(role)
    return entities, varchars


def translate_single_choice(df, translator_map, source_column=None, prefix=''):
    target = prefix + translator_map['int']
    if not source_column:
        source_column = translator_map['column']
    df[target] = df[source_column].apply(lambda x: translator_map[str(x)] if str(x) in translator_map else None)
    return target


def translate_free_text(df, source_column, target_column):
    df[target_column] = df[source_column].apply(lambda x: x.lower().strip() if x != '-99' else None)
    return target_column
