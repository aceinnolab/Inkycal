#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
test_internet_available
Copyright by aceisace
"""
import unittest
import socket
from unittest import mock
from inkycal.custom_functions.internet_available import internet_available

class TestInternetAvailable(unittest.TestCase):
    def test_internet_is_available(self):
        self.assertEqual(internet_available(), True)

    #patches socket to raise an error to test the excep portion of code
    @mock.patch('socket.socket', side_effect = socket.error)
    def test_internet_is_not_available(self, mock_internet_available):
        return_value = internet_available()
        self.assertEqual(return_value, False)

if __name__ == '__main__':
    unittest.main()
