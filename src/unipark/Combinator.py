import pandas as pd
from unipark.preprocessor import rename_pages


def combine_csvs_append_source(file_map):
    names = list(file_map.keys())
    csv, page_map = file_map[names[0]]
    df = pd.read_csv(csv, sep=';')
    df['survey']=names[0]
    if page_map:
        df = rename_pages(df, page_map)
    columns = {names[0] : df.columns.tolist()}
    for name in names[1:]:
        csv, page_map = file_map[name]
        other = pd.read_csv(csv, sep=';')
        other['survey']=name
        if page_map:
            other = rename_pages(other,page_map)
        columns[name] = other.columns.tolist()

        df = df.append(other, ignore_index=True, verify_integrity=True)

    # here on we simply check for columns that are in one csv only and print their names (if there are any)
    mutual = []
    for i in range(len(names)-1):
        for j in range(i+1,len(names)):
            for column in columns[names[i]]:
                if column in columns[names[j]]:
                    mutual.append(column)

    for name in names:
        unique = [x for x in columns[name] if x not in mutual]
        if unique:
            print('File {} contained {} unique columns:'.format(name, len(unique)))
            for line in unique:
               print('\t' + line)

    return df
