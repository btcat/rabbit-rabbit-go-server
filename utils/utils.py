# /usr/bin/python3
# -*- encoding: utf-8 -*-

import csv
import hashlib
import hmac
import os
import re

from babel.core import get_global
from babel.dates import format_date
from codecs import getincrementalencoder
from numbers import Number
from os.path import splitext, join
from io import open
from random import choice
import sys
import json

try:
    from cStringIO import StringIO
except:
    from io import StringIO

try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser

if sys.version_info[0] == 3:
    unichr = chr
    unicode = str
    IS_PY2 = False
    basestring = str
else:
    IS_PY2 = True

blocked_tags = ('script',
                'style')

ecma_unescape4_re = re.compile(r'%u([0-9a-fA-F]{4})', re.UNICODE)
ecma_unescape2_re = re.compile(r'%([0-9a-fA-F]{2})', re.UNICODE)

lang_to_lc_cache = dict()

def highlight_content(content, query):

    if not content:
        return None
    # ignoring html contents
    # TODO better html content detection
    if content.find('<') != -1:
        return content

    query = query.decode('utf-8')
    if content.lower().find(query.lower()) > -1:
        query_regex = u'({0})'.format(re.escape(query))
        content = re.sub(query_regex, '<span class="highlight">\\1</span>',
                         content, flags=re.I | re.U)
    else:
        regex_parts = []
        for chunk in query.split():
            if len(chunk) == 1:
                regex_parts.append(u'\\W+{0}\\W+'.format(re.escape(chunk)))
            else:
                regex_parts.append(u'{0}'.format(re.escape(chunk)))
        query_regex = u'({0})'.format('|'.join(regex_parts))
        content = re.sub(query_regex, '<span class="highlight">\\1</span>',
                         content, flags=re.I | re.U)

    return content


class HTMLTextExtractor(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_endtag(self, tag):
        if not self.tags:
            return

        if tag != self.tags[-1]:
            raise Exception("invalid html")

        self.tags.pop()

    def is_valid_tag(self):
        return not self.tags or self.tags[-1] not in blocked_tags

    def handle_data(self, d):
        if not self.is_valid_tag():
            return
        self.result.append(d)

    def handle_charref(self, number):
        if not self.is_valid_tag():
            return
        if number[0] in (u'x', u'X'):
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        if not self.is_valid_tag():
            return
        # codepoint = htmlentitydefs.name2codepoint[name]
        # self.result.append(unichr(codepoint))
        self.result.append(name)

    def get_text(self):
        return u''.join(self.result).strip()


def html_to_text(html):
    html = html.replace('\n', ' ')
    html = ' '.join(html.split())
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = getincrementalencoder(encoding)()

    def writerow(self, row):
        if IS_PY2:
            row = [s.encode("utf-8") if hasattr(s, 'encode') else s for s in row]
        self.writer.writerow(row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        if IS_PY2:
            data = data.decode("utf-8")
        else:
            data = data.strip('\x00')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        if IS_PY2:
            self.stream.write(data)
        else:
            self.stream.write(data.decode("utf-8"))
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_resources_directory(searx_directory, subdirectory, resources_directory):
    if not resources_directory:
        resources_directory = os.path.join(searx_directory, subdirectory)
    if not os.path.isdir(resources_directory):
        raise Exception(resources_directory + " is not a directory")
    return resources_directory


def get_themes(templates_path):
    """Returns available themes list."""
    themes = os.listdir(templates_path)
    if '__common__' in themes:
        themes.remove('__common__')
    return themes


def get_static_files(static_path):
    static_files = set()
    static_path_length = len(static_path) + 1
    for directory, _, files in os.walk(static_path):
        for filename in files:
            f = os.path.join(directory[static_path_length:], filename)
            static_files.add(f)
    return static_files


def get_result_templates(templates_path):
    result_templates = set()
    templates_path_length = len(templates_path) + 1
    for directory, _, files in os.walk(templates_path):
        if directory.endswith('result_templates'):
            for filename in files:
                f = os.path.join(directory[templates_path_length:], filename)
                result_templates.add(f)
    return result_templates


def dict_subset(d, properties):
    result = {}
    for k in properties:
        if k in d:
            result[k] = d[k]
    return result


def prettify_url(url, max_length=74):
    if len(url) > max_length:
        chunk_len = int(max_length / 2 + 1)
        return u'{0}[...]{1}'.format(url[:chunk_len], url[-chunk_len:])
    else:
        return url


# get element in list or default value
def list_get(a_list, index, default=None):
    if len(a_list) > index:
        return a_list[index]
    else:
        return default


def get_torrent_size(filesize, filesize_multiplier):
    try:
        filesize = float(filesize)

        if filesize_multiplier == 'TB':
            filesize = int(filesize * 1024 * 1024 * 1024 * 1024)
        elif filesize_multiplier == 'GB':
            filesize = int(filesize * 1024 * 1024 * 1024)
        elif filesize_multiplier == 'MB':
            filesize = int(filesize * 1024 * 1024)
        elif filesize_multiplier == 'KB':
            filesize = int(filesize * 1024)
        elif filesize_multiplier == 'TiB':
            filesize = int(filesize * 1000 * 1000 * 1000 * 1000)
        elif filesize_multiplier == 'GiB':
            filesize = int(filesize * 1000 * 1000 * 1000)
        elif filesize_multiplier == 'MiB':
            filesize = int(filesize * 1000 * 1000)
        elif filesize_multiplier == 'KiB':
            filesize = int(filesize * 1000)
    except:
        filesize = None

    return filesize


def convert_str_to_int(number_str):
    if number_str.isdigit():
        return int(number_str)
    else:
        return 0


# convert a variable to integer or return 0 if it's not a number
def int_or_zero(num):
    if isinstance(num, list):
        if len(num) < 1:
            return 0
        num = num[0]
    return convert_str_to_int(num)



def _get_lang_to_lc_dict(lang_list):
    key = str(lang_list)
    value = lang_to_lc_cache.get(key, None)
    if value is None:
        value = dict()
        for lc in lang_list:
            value.setdefault(lc.split('-')[0], lc)
        lang_to_lc_cache[key] = value
    return value


# auxiliary function to match lang_code in lang_list
def _match_language(lang_code, lang_list=[], custom_aliases={}):
    # replace language code with a custom alias if necessary
    if lang_code in custom_aliases:
        lang_code = custom_aliases[lang_code]

    if lang_code in lang_list:
        return lang_code

    # try to get the most likely country for this language
    subtags = get_global('likely_subtags').get(lang_code)
    if subtags:
        subtag_parts = subtags.split('_')
        new_code = subtag_parts[0] + '-' + subtag_parts[-1]
        if new_code in custom_aliases:
            new_code = custom_aliases[new_code]
        if new_code in lang_list:
            return new_code

    # try to get the any supported country for this language
    return _get_lang_to_lc_dict(lang_list).get(lang_code, None)


# get the language code from lang_list that best matches locale_code
def match_language(locale_code, lang_list=[], custom_aliases={}, fallback='en-US'):
    # try to get language from given locale_code
    language = _match_language(locale_code, lang_list, custom_aliases)
    if language:
        return language

    locale_parts = locale_code.split('-')
    lang_code = locale_parts[0]

    # try to get language using an equivalent country code
    if len(locale_parts) > 1:
        country_alias = get_global('territory_aliases').get(locale_parts[-1])
        if country_alias:
            language = _match_language(lang_code + '-' + country_alias[0], lang_list, custom_aliases)
            if language:
                return language

    # try to get language using an equivalent language code
    alias = get_global('language_aliases').get(lang_code)
    if alias:
        language = _match_language(alias, lang_list, custom_aliases)
        if language:
            return language

    if lang_code != locale_code:
        # try to get language from given language without giving the country
        language = _match_language(lang_code, lang_list, custom_aliases)

    return language or fallback


def new_hmac(secret_key, url):
    try:
        secret_key_bytes = bytes(secret_key, 'utf-8')
    except TypeError as err:
        if isinstance(secret_key, bytes):
            secret_key_bytes = secret_key
        else:
            raise err
    if sys.version_info[0] == 2:
        return hmac.new(bytes(secret_key), url, hashlib.sha256).hexdigest()
    else:
        return hmac.new(secret_key_bytes, url, hashlib.sha256).hexdigest()


def to_string(obj):
    if isinstance(obj, basestring):
        return obj
    if isinstance(obj, Number):
        return unicode(obj)
    if hasattr(obj, '__str__'):
        return obj.__str__()
    if hasattr(obj, '__repr__'):
        return obj.__repr__()


def ecma_unescape(s):
    """
    python implementation of the unescape javascript function

    https://www.ecma-international.org/ecma-262/6.0/#sec-unescape-string
    https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/unescape
    """
    # s = unicode(s)
    # "%u5409" becomes "吉"
    s = ecma_unescape4_re.sub(lambda e: unichr(int(e.group(1), 16)), s)
    # "%20" becomes " ", "%F3" becomes "ó"
    s = ecma_unescape2_re.sub(lambda e: unichr(int(e.group(1), 16)), s)
    return s
