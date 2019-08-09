# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Sanic
from api.searchapi import searchbluepoint

app = Sanic(load_env=True)

app.blueprint(searchbluepoint)

app.run()