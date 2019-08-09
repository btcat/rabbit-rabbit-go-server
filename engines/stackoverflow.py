# /usr/bin/python3
# -*- encoding: utf-8 -*-

from requests import get
import random
from lxml import html
from utils.xpath import extract_text
from utils.url_utils import urlencode, urljoin

class StackoverflowEngine():
    def __init__(self):
        self.url = 'https://stackoverflow.com/'
        self.search_url = 'https://stackoverflow.com/search?q={query}&page={pageno}'
        self.results_xpath = '//div[contains(@class,"question-summary")]'
        self.link_xpath = './/div[@class="result-link"]//a|.//div[@class="summary"]//h3//a'
        self.content_xpath = './/div[@class="exvcerpt"]'
    
    def search(self, keyword="", pageno=1):
        results = []

        for i in range(5):
            if results != []:
                break
            results = self.query(keyword, pageno)
        
        return results
    
    def query(self, keyword="", pageno=1):
        resp = get(self.search_url.format(query=keyword, pageno=pageno), headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }, proxies={"http":"{}.{}.{}.{}".format(random.randint(10, 99), random.randint(10, 99), random.randint(10, 99), random.randint(10, 99))})
        results = []

        dom = html.fromstring(resp.text)

        # parse results
        for result in dom.xpath(self.results_xpath):
            link = result.xpath(self.link_xpath)[0]
            href = urljoin(self.url, link.attrib.get('href'))
            title = extract_text(link)
            content = extract_text(result.xpath(self.content_xpath))

            # append result
            results.append({'url': href,
                            'title': title,
                            'content': content})

        # return results
        return results