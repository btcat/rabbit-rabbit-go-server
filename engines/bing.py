# /usr/bin/python3
# -*- encoding: utf-8 -*-

class BingEngine():
    def __init__(self):
        self.base_url = "https://www.bing.com/"

    def _get_offset_from_pageno(self, pageno):
        return (pageno - 1) * 10 + 1

    def query(self, keyword="", pageno=1):
