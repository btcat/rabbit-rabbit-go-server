# /usr/bin/python3
# -*- encoding: utf-8 -*-

from sanic import Blueprint
from sanic.response import json
from mergeor.mergeor import Mergeor

searchbluepoint = Blueprint('search', url_prefix='/search')
mergeor = Mergeor()

@searchbluepoint.route("/query", methods=["POST",])
def search(request):
    keyword = request.form.get("keyword")
    pageno = request.form.get("pageno")
    result = mergeor.search(keyword, int(pageno))
    
    return json({
        'code': 0,
        'message': 'Search OK.',
        'results': result,
    })