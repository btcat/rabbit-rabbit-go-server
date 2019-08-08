# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Sanic
from os import environ
import config
from engines.bing import BingEngine

print(BingEngine().query("大白兔"))

#app = Sanic()

#app.run(host="0.0.0.0", port=environ["PORT"])