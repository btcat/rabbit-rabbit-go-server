# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Sanic
from os import environ
import config
from engines.stackoverflow import StackoverflowEngine

a = (StackoverflowEngine().search(input("a:"), 2))
print(a)

#app = Sanic()

#app.run(host="0.0.0.0", port=environ["PORT"])