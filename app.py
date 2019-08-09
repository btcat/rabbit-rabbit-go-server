# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Sanic
from os import environ
import config
from mergeor.mergeor import Mergeor

print(Mergeor().search("bug", 1))

#app = Sanic()

#app.run(host="0.0.0.0", port=environ["PORT"])