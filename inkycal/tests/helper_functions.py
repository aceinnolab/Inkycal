#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Helper functions for inkycal tests.
Copyright by aceisace
"""
import logging
import sys

from os.path import exists
from inkycal.modules.inky_image import Inkyimage

preview =  Inkyimage.preview
merge = Inkyimage.merge

def get_environment():
  # Check if this is running on the Raspberry Pi
  environment = None
  envir_path = '/sys/firmware/devicetree/base/model'
  if exists(envir_path):
    with open(envir_path) as file:
      if 'Raspberry' in file.read():
        environment = 'Raspberry'
  return environment
