from unipark.Combinator import combine_csvs_append_source
from datetime import date

files = {
    'LinkedIn': ('../data/LinkedIn_data_project_720014_2020_11_23.csv',
                 { # page map
                     4584574: 10,
                     4584575: 20,
                     4584576: 30,
                     4584577: 40,
                     4584578: 41,
                     4584579: 45,
                     4584580: 50,
                     4584581: 60,
                     4584582: 70,
                 }),
    'Reddit': ('../data/Reddit_data_project_685539_2020_10_27.csv',
               { # page map
                   4342262: 10,
                   4342263: 20,
                   4342264: 30,
                   4342265: 40,
                   4342266: 41,
                   4342267: 45,
                   4342268: 50,
                   4342269: 60,
                   4342270: 70
               }),
    'Contacts': ('../data/Contacts_data_project_685913_2020_10_27.csv',
                 { # page map
                     4343844: 10,
                     4343845: 20,
                     4343846: 30,
                     4343847: 40,
                     4343848: 41,
                     4343849: 45,
                     4343850: 50,
                     4343851: 60,
                     4343852: 70
                 })
}
combined_file = date.today().strftime('../data/combined_data_%Y_%m_%d.csv')

if __name__ == "__main__":
    # execute only if run as a script

    df = combine_csvs_append_source(files)
    df.to_csv(combined_file, sep=';')

    print('done')
