import re

import requests
from lxml.html import fromstring

def search(id):
    response = _submit_search(id)
    if response.status_code != 200:
        raise RuntimeError('failed to fetch data')

    root = fromstring(response.text.encode())

    if not _has_result(root):
        raise RuntimeError('wrong id')

    return _extract_book(root)

def _submit_search(id):
    return requests.post(
        'http://information.hanyang.ac.kr/ansan/jsp/sea/detailinfo/SearchDetailController.jsp',
        headers={
            'user-agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)'
        },
        data={
            'menuid': '200000000008',
            'serialno': '200000000001',
            'resultindex': 0,
            'act': '',
            'model': '',
            'method': '',
            'websysdiv': 'TOT',
            'sysdivs': 'CAT',
            'limit01': '',
            'location': '',
            'mainbackcnt': -1,
            'briefbackcnt': 0,

            'controlnos': id,
        }
    )

def _has_result(root):
    return len(root.xpath('//table[@id="detail_search"]//td[@class="board_nametext"]')) > 0

def _extract_book(root):
    return {
        'title': _extract_title(root),
        'authors': _extract_authors(root),
        'publisher': _extract_publisher(root),
        'borrowing_informations': _extract_borrowing_informations(root),
    }

def _extract_title(root):
    return root.xpath('//form[@name="frm"]//input[@name="title"]')[0].get('value')

def _extract_authors(root):
    elements = root.xpath('//table/tr[@class="board_line1"][td="개인저자"]//a[@class="boardtitle"]')
    if len(elements) == 0:
        elements = root.xpath('//table/tr[@class="board_line1"][td="단체저자명"]//a[@class="boardtitle"]')

    authors = []
    for element in elements:
        if not re.search(r'^\s*\d*\s*\-\s*\d*\s*$', element.text_content()):
            authors.append(element.text_content().strip())

    return authors

def _extract_publisher(root):
    element = root.xpath('//table/tr[@class="board_line1"][td="발행사항"]//td')[1]
    match = re.search(r'[^:]*\:(.+?)\,.*\d+', element.text_content())

    return match.group(1).strip()

def _extract_borrowing_informations(root):
    elements = root.xpath('//table[@id="detail_search"]//table[@class="board_size"]//tr[@class="board_line1"]')

    informations = []
    for element in elements:
        informations.append(_extract_borrowing_information(element.xpath('td')))

    return informations

def _extract_borrowing_information(elements):
    place_and_section = _extract_place_and_section(elements[3].text_content())

    information = {
        'call_number': elements[2].text_content().strip(),
        'place': place_and_section['place'],
        'section': place_and_section['section'],
        'is_able_to_borrow': (elements[4].text_content().strip() == '대출가능'),
        'return_due_date': elements[5].text_content().strip(),
    }

    if not information['return_due_date']:
        del information['return_due_date']

    return information

def _extract_place_and_section(where):
    match = re.search(r'(박물관|백남학술정보관|법학학술정보관|의학학술정보관|ERICA학술정보관)/(.+?)/', where)

    return {
        'place': match.group(1),
        'section': match.group(2)
    }