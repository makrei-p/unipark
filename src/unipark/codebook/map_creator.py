

def get_map_for_multi_selection(lines, start, end):
    var_translator = {}
    for line in lines[start:end:3]:
        if '\t' in line:
            splits = line[:-1].split('\t')
            var_translator[splits[0]]=(splits[2], splits[3])
    return var_translator


def get_map_for_single_selection(lines, start, end):
    return dict([x[:-1].split('\t')[2:4] for x in lines[start:end]])