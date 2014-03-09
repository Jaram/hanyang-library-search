import time
import re

import requests
from lxml.etree import fromstring

from library.books.query import search_type_information, generate_search_query, generate_display_query

def search(type, keyword, page=1):
    response = _submit_search(type, keyword, page)
    if response.status_code != 200:
        raise RuntimeError('failed to fetch data')

    root = fromstring(response.text.encode())
    
    return {
        'books': _extract_books(root),
        'count': int(root.find('count').text)
    }

def _submit_search(type, keyword, page):
    return requests.post(
        'http://information.hanyang.ac.kr/ansan/jsp/sea/briefresult/BriefResult.jsp?timeStamp={0:d}'.format(int(time.time() * 1000)),
        headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48 Safari/537.36'
        },
        data={
            'menuid': '200000000008',
            'websysdiv': 'TOT',
            'countPerPage': 20,
            'formatQuery': '',
            'sortQuery': '',
            'statistics': '',
            'isDBSearch': '',

            'searchType': search_type_information[type]['description'],
            'kindOfSearch': search_type_information[type]['description'],
            'queryString': generate_search_query(type, keyword),
            'realQueryString': '({0})'.format(generate_search_query(type, keyword)),
            'displayQuery': generate_display_query(type, keyword),
            'selPageIndex': page
        }
    )

def _extract_books(root):
    books = []

    for data in root.find('list').findall('data'):
        books.append(_extract_book(data))

    return books

def _extract_book(data):
    return {
        'id': data.get('CTRL'),
        'title': _extract_title(data),
        'author': data.find('DISP02').text,
        'publisher': data.find('DISP03').text,
        'call_number': data.find('DISP04').text,
        'borrowing_informations': _extract_borrowing_informations(data)
    }

def _extract_title(data):
    return re.sub(r'\[\d+m(.+?)\[\d+m', r'\1', data.find('DISP01').text)

def _extract_borrowing_informations(data):
    raw_information = data.find('DISP07').text
    raw_information = re.sub(r'<[^>]+>', '', raw_information) # strip html tags

    informations = []

    matches = re.finditer(r'(박물관|백남학술정보관|법학학술정보관|의학학술정보관|ERICA학술정보관)\[([^\]]+)\]\[([^\]]+)\]', raw_information)
    for match in matches:
        informations.append({
            'place': match.group(1),
            'section': match.group(2),
            'is_able_to_borrow': (match.group(3) == '대출가능')
        })

    return informations
