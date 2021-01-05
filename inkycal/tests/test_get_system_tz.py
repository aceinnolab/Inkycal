#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
test_get_system_tz
Copyright by aceisace
"""

import unittest
from unittest import mock
import time
import os

from inkycal.custom_functions.get_system_tz import get_system_tz

class TestGetSystemTZ(unittest.TestCase):
    #mocked OS to return Eastern Standard Time
    #note: test works fine in EST or in linux systems. Does not work in Windows
    @mock.patch.dict(os.environ, {'TZ': 'EST+05EDT,M4.1.0,M10.5.0'})
    @mock.patch.object(time, 'tzname', return_value = 'Eastern Daylight Time')
    def test_get_system_tz(self, mock_time):
        self.assertEqual(time.tzname[1], get_system_tz())

# doesn't test the except block of get_system_tz. From looking at the docs,
# I'm not sure that it's possible to raise through normal use.

if __name__ == '__main__':
    unittest.main()




@mock.patch.dict(os.environ, {"TZ": None})
def test_get_system_tz(mock_time):
    assertEqual(time.tzname[1], get_system_tz())