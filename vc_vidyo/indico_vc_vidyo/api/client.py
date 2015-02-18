# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

import re

from suds.client import Client
from suds.transport.https import HttpAuthenticated

from indico_vc_vidyo.api.cache import SudsCache

DEFAULT_CLIENT_TIMEOUT = 30
AUTOMUTE_API_PROFILE = "NoAudioAndVideo"


class ClientBase(object):
    def __init__(self, wsdl, settings):
        transport = HttpAuthenticated(username=settings.get('username'), password=settings.get('password'),
                                      timeout=DEFAULT_CLIENT_TIMEOUT)
        self.client = Client(wsdl, cache=SudsCache(), transport=transport, location=re.sub(r'\?wsdl$', '', wsdl))

    @property
    def soap(self):
        return self.client.service


class UserClient(ClientBase):
    def __init__(self, settings):
        super(UserClient, self).__init__(settings.get('user_api_wsdl'), settings)


class AdminClient(ClientBase):
    def __init__(self, settings):
        super(AdminClient, self).__init__(settings.get('admin_api_wsdl'), settings)

    def create_room_object(self, **kwargs):
        room = self.client.factory.create('Room')

        for key, value in kwargs.iteritems():
            setattr(room, key, value)

        return room

    def find_room(self, extension):
        filter_ = self.client.factory.create('Filter')
        filter_.query = extension
        filter_.dir = 'DESC'

        return self.soap.getRooms(filter_).room

    def add_room(self, room):
        self.soap.addRoom(room)

    def set_automute(self, room_id, status):
        if status:
            self.soap.setRoomProfile(room_id, AUTOMUTE_API_PROFILE)
        else:
            self.soap.removeRoomProfile(room_id)
