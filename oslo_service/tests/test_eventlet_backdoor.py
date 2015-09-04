# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Unit Tests for eventlet backdoor
"""
import errno
import socket

import eventlet
import mock

from oslo_service import eventlet_backdoor
from oslo_service.tests import base


class BackdoorPortTest(base.ServiceBaseTestCase):

    @mock.patch.object(eventlet, 'spawn')
    @mock.patch.object(eventlet, 'listen')
    def test_backdoor_port(self, listen_mock, spawn_mock):
        self.config(backdoor_port=1234)
        sock = mock.MagicMock()
        sock.getsockname.return_value = ('127.0.0.1', 1234)
        listen_mock.return_value = sock
        port = eventlet_backdoor.initialize_if_enabled(self.conf)
        self.assertEqual(port, 1234)

    @mock.patch.object(eventlet, 'spawn')
    @mock.patch.object(eventlet, 'listen')
    def test_backdoor_port_inuse(self, listen_mock, spawn_mock):
        self.config(backdoor_port=2345)
        listen_mock.side_effect = socket.error(errno.EADDRINUSE, '')
        self.assertRaises(socket.error,
                          eventlet_backdoor.initialize_if_enabled, self.conf)

    @mock.patch.object(eventlet, 'spawn')
    @mock.patch.object(eventlet, 'listen')
    def test_backdoor_port_range(self, listen_mock, spawn_mock):
        self.config(backdoor_port='8800:8899')
        sock = mock.MagicMock()
        sock.getsockname.return_value = ('127.0.0.1', 8800)
        listen_mock.return_value = sock
        port = eventlet_backdoor.initialize_if_enabled(self.conf)
        self.assertEqual(port, 8800)

    @mock.patch.object(eventlet, 'spawn')
    @mock.patch.object(eventlet, 'listen')
    def test_backdoor_port_range_one_inuse(self, listen_mock, spawn_mock):
        self.config(backdoor_port='8800:8900')
        sock = mock.MagicMock()
        sock.getsockname.return_value = ('127.0.0.1', 8801)
        listen_mock.side_effect = [socket.error(errno.EADDRINUSE, ''), sock]
        port = eventlet_backdoor.initialize_if_enabled(self.conf)
        self.assertEqual(port, 8801)

    @mock.patch.object(eventlet, 'spawn')
    @mock.patch.object(eventlet, 'listen')
    def test_backdoor_port_range_all_inuse(self, listen_mock, spawn_mock):
        self.config(backdoor_port='8800:8899')
        side_effects = []
        for i in range(8800, 8900):
            side_effects.append(socket.error(errno.EADDRINUSE, ''))
        listen_mock.side_effect = side_effects
        self.assertRaises(socket.error,
                          eventlet_backdoor.initialize_if_enabled, self.conf)

    def test_backdoor_port_reverse_range(self):
        self.config(backdoor_port='8888:7777')
        self.assertRaises(eventlet_backdoor.EventletBackdoorConfigValueError,
                          eventlet_backdoor.initialize_if_enabled, self.conf)

    def test_backdoor_port_bad(self):
        self.config(backdoor_port='abc')
        self.assertRaises(eventlet_backdoor.EventletBackdoorConfigValueError,
                          eventlet_backdoor.initialize_if_enabled, self.conf)
