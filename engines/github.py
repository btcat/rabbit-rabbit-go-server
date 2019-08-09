# /usr/bin/python3
# -*- encoding: utf-8 -*-

from json import loads
from requests import get
import random

class GithubEngine():
    def __init__(self):
        self.search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&q={query}'
        self.accept_header = 'application/vnd.github.preview.text-match+json'

    def query(self, keyword="", pageno=1):
        resp = get(self.search_url.format(query=keyword), headers={
            'Accept': self.accept_header,
        }, proxies={"http":"{}.{}.{}.{}".format(random.randint(10, 99), random.randint(10, 99), random.randint(10, 99), random.randint(10, 99))})

        results = []

        search_res = loads(resp.text)

        # check if items are recieved
        if 'items' not in search_res:
            return []

        # parse results
        for res in search_res['items']:
            title = res['name']
            url = res['html_url']

            if res['description']:
                content = res['description'][:500]
            else:
                content = ''

            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content})

        try:
            offset = pageno * 10
            return results[1+offset-11:offset]
        except:
            return []