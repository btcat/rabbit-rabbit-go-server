# /usr/bin/python3
# -*- encoding: utf-8 -*-

from requests import get
from utils.xpath import extract_text
from utils.url_utils import urlencode
from lxml import html
from utils.utils import match_language
import string
import random

class BingEngine():
    def __init__(self):
        self.base_url = "https://cn.bing.com/"
        self.search_string = "search?q={query}&first={offset}"

    def _get_offset_from_pageno(self, pageno):
        return (pageno - 1) * 10 + 1

    def query(self, keyword="", pageno=1):
        results = []
        result_len = 0

        offset = self._get_offset_from_pageno(pageno)
        querystring = "{}".format(keyword)

        search_path = self.search_string.format(
            query=querystring,
            offset=offset,
        )

        resp = get(self.base_url + search_path, headers={
            'user-agent': ''.join(random.sample(string.ascii_letters + string.digits, 24))
        }, proxies={"http":"{}.{}.{}.{}".format(random.randint(10, 99), random.randint(10, 99), random.randint(10, 99), random.randint(10, 99))})

        dom = html.fromstring(resp.text)
        # parse results
        for result in dom.xpath('//div[@class="sa_cc"]'):
            link = result.xpath('.//h3/a')[0]
            url = link.attrib.get('href')
            title = extract_text(link)
            content = extract_text(result.xpath('.//p'))

            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content})

        # parse results again if nothing is found yet
        for result in dom.xpath('//li[@class="b_algo"]'):
            link = result.xpath('.//h2/a')[0]
            url = link.attrib.get('href')
            title = extract_text(link)
            content = extract_text(result.xpath('.//p'))

            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content})

        try:
            result_len_container = "".join(dom.xpath('//span[@class="sb_count"]/text()'))
            result_len_container = utils.to_string(result_len_container)
            if "-" in result_len_container:
                # Remove the part "from-to" for paginated request ...
                result_len_container = result_len_container[result_len_container.find("-") * 2 + 2:]

            result_len_container = re.sub('[^0-9]', '', result_len_container)
            if len(result_len_container) > 0:
                result_len = int(result_len_container)
        except Exception as e:
            pass

        return results, result_len
