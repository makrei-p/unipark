import pandas as pd
import re

# styles
qtype_id_to_qtype_translator = {
    111: 'single',
    121: 'multiple',
    131: 'single',
    141: 'free',
    142: 'free',
    143: 'freematrix',
    311: 'matrix',
    411: 'rank'
}


def get_map_for_multi_selection(lines, start, end):
    var_translator = {}
    for line in lines[start:end:3]:
        if '\t' in line:
            splits = line.split('\t')
            value = (splits[2], splits[3])
            var_translator[splits[1]] = value
            # vars hve alt name splits[0] --> add both keys with same value
            var_translator[splits[0]] = value
    return var_translator


def get_map_for_single_selection(lines, start, end):
    def get_tuple(x):
        # take last two columns (int, str name)
        tup = x.split('\t')[2:4]
        if not tup[1]:
            tup[1] = tup[0]
        return tup

    ret = dict([get_tuple(x) for x in lines[start:end]])
    ret['alt_column'], ret['column'] = lines[start].split('\t')[0:2]
    return ret


def get_map_for_freetext(lines, start, end):
    splits = lines[start].split('\t')
    return {
        'alt_columns': splits[0],
        'column': splits[1],
        'varchar': splits[3]
    }

def get_map_for_freematrix(lines, start, end):
    def get_tuple(x):
        option_elements = x.split('\t')
        variable = option_elements[1]
        name = option_elements[3].split(':')[1].split('(')[0].strip()
        return [variable, name]

    ret = dict([get_tuple(line) for line in lines[start:end]])
    return ret


def get_map_for_ranked(lines, start, end):
    ret = {}
    minimum = None
    maximum = None
    while start != end:
        line = lines[start]
        if line.startswith('v_'):
            splits = line.split('\t')
            ret[splits[0]] = (splits[2], splits[3])
        elif line.strip():
            splits = line.split('\t')
            num = int(splits[3])
            if minimum is None or minimum > num:
                minimum = num
            if maximum is None or maximum < num:
                maximum = num
        start += 1
    ret['range_min'] = minimum
    ret['range_max'] = maximum
    return ret


def get_map_for_matrix(lines, start, end):
    # matrix is basically a list of single questions so lets handle it that way
    subs = []

    def is_headline(x):  # non-headlines start with '\t\t'
        return bool(x.split('\t')[0])

    sub_start, sub_end = start, start + 1
    while sub_end < end:
        # search for sub-questions (sub_end is exclusive last line of q --> first line of next)
        while sub_end < end and not is_headline(lines[sub_end]):
            sub_end += 1
        subs.append(get_map_for_single_selection(lines, sub_start, sub_end))
        sub_start = sub_end
        sub_end += 1
    ret = {'subs': subs}
    return ret


class CodeBookParser:
    page_re = r'^[0-9]*\.?[0-9]? Seite: (.*) \(PGID ([0-9]{7})\)$'
    question_re = r'^(.*) \(q_([0-9]{7}) - Typ ([0-9]{3})\)$'

    def __init__(self, csv, reassign_page_id=False):
        with open(csv) as file:
            self.lines = pd.Series(file.readlines())
        self.lines = self.lines.apply(lambda x: x[:-1])
        self.reassign_page_id = reassign_page_id
        self._questions_ = None
        self._pages_ = None
        self.codebook = {
            'type': 'survey',
            'title': self.get_headline(),
            'pages': self.get_pagebooks()
        }

    def get_codebook(self):
        return self.codebook

    def get_headline(self):
        return self.lines[0]

    def get_page_lines(self):
        if not self._pages_:
            hits = []
            for i in range(len(self.lines)):
                found = re.findall(self.page_re, self.lines[i])
                if found:
                    if self.reassign_page_id:
                        found[0] = [found[0][0], str(self.reassign_page_id(found[0][1]))]
                    hits.append([i, *found[0]])
            self._pages_ = hits
        return self._pages_

    def get_question_lines(self):
        if not self._questions_:
            hits = []
            for i in range(len(self.lines)):
                found = re.findall(self.question_re, self.lines[i])
                if found:
                    hits.append([i, *found[0]])
            self._questions_ = hits
        return self._questions_

    def get_pagebooks(self):
        pages = self.get_page_lines()
        ret = []
        for i in range(len(pages) - 1):
            ret.append(self.get_pagebook(*pages[i], pages[i + 1][0]))
        ret.append(self.get_pagebook(*pages[-1]))
        return ret

    def get_pagebook(self, start_line, title, page_id, end_line=-1):
        questions = [x for x in self.get_question_lines() if x[0] > start_line and (end_line == -1 or end_line > x[0])]
        ret = {
            'type': 'page',
            'title': title,
            'id': page_id,
            'questions': [self.get_questionbook(*x) for x in questions]
        }
        return ret

    def get_questionbook(self, start_line, title, question_id, style_id):
        ret = {
            'type': 'question',
            'style_id': style_id,
            'style': qtype_id_to_qtype_translator.get(int(style_id), style_id),
            'title': title,
            'id': question_id
        }
        end_line = start_line
        while end_line + 2 < len(self.lines) and (self.lines[end_line + 1] or self.lines[end_line]):
            end_line += 1

        if ret['style'] == 'single':
            ret = {**ret, **get_map_for_single_selection(self.lines, start_line + 1, end_line)}
        elif ret['style'] == 'multiple':
            ret = {**ret, **get_map_for_multi_selection(self.lines, start_line + 1, end_line + 1)}
        elif ret['style'] == 'free':
            ret = {**ret, **get_map_for_freetext(self.lines, start_line + 1, end_line)}
        elif ret['style'] == 'freematrix':
            ret = {**ret, **get_map_for_freematrix(self.lines, start_line + 1, end_line)}
        elif ret['style'] == 'rank':
            ret = {**ret, **get_map_for_ranked(self.lines, start_line + 1, end_line)}
        elif ret['style'] == 'matrix':
            ret = {**ret, **get_map_for_matrix(self.lines, start_line + 1, end_line)}
        else:
            print(f'unknown question type {ret["style"]}')
        return ret
