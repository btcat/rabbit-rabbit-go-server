# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Sanic
from os import environ
import config
from engines.bing import BingEngine

for i in range(50):
    a, b = (BingEngine().search("app"))
    if a == []:
        print(a)

#app = Sanic()

#app.run(host="0.0.0.0", port=environ["PORT"])