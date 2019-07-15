# This file is part of the CERN Indico plugins.
# Copyright (C) 2014 - 2019 CERN
#
# The CERN Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

import json
import re
import requests

from marshmallow import Schema, fields, post_load

from flask import redirect
from flask_pluginengine import current_plugin
from werkzeug.urls import url_encode

from indico.core.db import db
from indico.core.plugins import get_plugin_template_module
from indico_search import SearchEngine




class Result(object):
    def __init__(self, title, url, author):
    self.title = title  
    self.url = url  
    self.author = author    


class ResultSchema(Schema):
    title = fields.Str()
    url = fields.Url()
    author = fields.Str()

    @post_load
    def make_user(self, data):
        return Result(**data)



#FIELD_MAP = {'title': 'titlereplica',
#             'abstract': 'description',
#             'author': 'authors',
#             'affiliation': 'companies',
#             'keyword': 'keywords'}


class JSONSearchEngine(SearchEngine):
   
    @property
    def url(self):
    return current_plugin.settings.get('search_url')

    def process(self):
        out = self._query()
        out = self._deserialize(out)
        return out

    def _query(self):
        endpoint = '/api/records/'  # FIXME, it has to be the same endpoint set by the livesync plugin
        url = '{0}{1}'.format(self.url, endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer <ACCESS_TOKEN>'
        }
        param = # FIXME !!!!!!!!!!
        response = requests.get(url, headers=headers, param=param)
        if response.ok:
            content = json.loads(response.content)
            return content


    def _deserialize(self, content):
        schema = ResultSchema()
        out = []
        for item in content:
            result = schema.load(item)
            out.append(result.data)
        return out
    

