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

        # search values
        self.username = self.user.name
        self.useremail = self.user.email
        self.query_phrase = self.values['phrase']
        self.query_start_date = self.values['start_date']  # datetime.date object
        self.query_end_date = self.values['end_date']  # datetime.date object
        self.query_field = self.values['field']

        query = self._build_query()
        out = self._query(query)
        return out


   def _build_query(self):

        phrase = self.values['phrase']
        field = self.values['field']
        start_date = self.values['start_date']
        end_date = self.values['end_date']

        # change white spaces by + sign in phrase
        phrase = '+OR+'.join([x.strip() for x in phrase.split()])

        if field:
            qphrase = '%s:(%s)' %(field, phrase)
        else:
            # FIXME: is this correct?
            qphrase = '(%s)' %phrase

        # format the date range
        if start_date and end_date:
            qdate = '+AND+date:[%s+TO+%s]' %(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if start_date and not end_date:
            qdate = '+AND+date:[%s+TO+*}' %start_date.strftime('%Y-%m-%d')
        if not start_date and end_date:
            qdate = '+AND+date:{*+TO+%s]' %end_date.strftime('%Y-%m-%d')
        if not start_date and not end_date:
            qdate = ''

        query = 'q=' + qphrase + qdate
        print >> open('/tmp/log', 'a'), "indico_search_json/engine.py/JSONSearchEngine.process query string %s" %query
        return query


    def _query(self, query):
        endpoint = '/api/records/'  # FIXME, it has to be the same endpoint set by the livesync plugin
        url = '{0}{1}'.format(self.url, endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer <ACCESS_TOKEN>'
        }
        response = requests.get(url, headers=headers, paramsquery)
        if response.ok:
            content = json.loads(response.content)
            return content


