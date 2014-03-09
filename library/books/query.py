import re

search_type_information = {
    'keyword': {
        'index': 2,
        'description': 'KWRD',
        'representation': '키워드검색',
        'range_index': 0,
        'range_description': '전체',
        'equal_index': 3
    },

    'front': {
        'index': 1,
        'description': 'FRNT',
        'representation': '전방일치검색',
        'range_index': 0,
        'range_description': '전체',
        'equal_index': 1
    },

    'exact': {
        'index': 1,
        'description': 'EXCT',
        'representation': '완전일치검색',
        'range_index': 0,
        'range_description': '전체',
        'equal_index': 3
    }
}

def generate_search_query(type, keyword):
    keyword = _filter_keyword(keyword)
    if not keyword:
        raise RuntimeError('short keyword')

    information = search_type_information[type]
    if information['index'] == 1:
        return '[{0},TOT,{1},{2},{3}]'.format(
            keyword, 
            information['index'],
            information['range_index'],
            information['equal_index']
        )

    query = ''

    or_tokens = keyword.split(' or ')
    for or_token in or_tokens:
        and_tokens = or_token.split(' and ')
        for and_token in and_tokens:
            query += '[{0},TOT,{1},{2},{3}]and'.format(
                and_token,
                information['index'],
                information['range_index'],
                information['equal_index']
            )

        query = '({0})or'.format(query[:-3])

    return query[:-2]

def generate_display_query(type, keyword):
    information = search_type_information[type]

    return '[{0}/ {1}:{2}]'.format(
        information['representation'],
        information['range_description'],
        keyword
    )

def _filter_keyword(keyword):
    keyword = re.sub(r'[\(\)\[\]\{\}\!\#\$\%\&\*\/\?\`\|\~\<\>\@\^\\\'\"\,\:\;\=\.]', '', keyword);

    # I don't know why the below codes need. I just mimicked the library's code
    if len(keyword) <= 3:
        keyword = re.sub(r'\b(a|an|de|for|in|of|the) ?\b', '', keyword, flags=re.IGNORECASE)

    return keyword.strip()