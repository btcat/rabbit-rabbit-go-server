# /usr/bin/python3
# -*- encoding: utf-8 -*-

from engines.github import GithubEngine
from engines.stackoverflow import StackoverflowEngine

class Mergeor():
    def __init__(self):
        self.github = GithubEngine()
        self.stackoverflow = StackoverflowEngine()

    def search(self, keyword="", pageno=1):
        github = self.github.search(keyword, pageno)
        stackover = self.github.search(keyword, pageno)
        return {
            'github': github,
            'stackoverflow': stackover,
        }