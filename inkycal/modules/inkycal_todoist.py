#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
todoist module for Inky-Calendar Project
Copyright by aceisace
"""

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

try:
  import todoist
except ImportError:
  print('todoist is not installed! Please install with:')
  print('pip3 install todoist-python')

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.ERROR)


api = todoist.TodoistAPI('your api key')
api.sync()

# Print name of author
print(api.state['user']['full_name']+'\n')


tasks = (task.data for task in api.state['items'])

for _ in tasks:
  print('task: {} is {}'.format(_['content'], 'done' if _['checked'] == 1 else 'not done'))
