# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Sanic
from os import environ
import config
from engines.github import GithubEngine

a = (GithubEngine().query(input("a:"), 1))
print(a)

#app = Sanic()

#app.run(host="0.0.0.0", port=environ["PORT"])