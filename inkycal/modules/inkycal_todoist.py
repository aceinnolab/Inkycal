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

class Todoist(inkycal_module):
  """Todoist api class
  parses todo's from api-key
  """

  name = "Inkycal Todoist"

  requires = {
    'api_key': {
      "label":"Please enter your Todoist API-key",
      },
  }

  optional = {
    'project_filter': {
      "label":"Show Todos only from following project (separated by a comma). Leave empty to show "+
      "todos from all projects",
    }
  }

  def __init__(self, config):
    """Initialize inkycal_rss module"""

    super().__init__(config)

    config = config['config']

    # Check if all required parameters are present
    for param in self.requires:
      if not param in config:
        raise Exception('config is missing {}'.format(param))

    # module specific parameters
    self.api_key = config['api_key']

    # only show todos from these projects
    if config['project_filter']:
      self.project_filter = config['project_filter'].split(',')
    else:
      self.project_filter = config['project_filter']      

    self._api = todoist.TodoistAPI(config['api_key'])
    self._api.sync()

    # give an OK message
    print('{0} loaded'.format(self.name))

  def _validate(self):
    """Validate module-specific parameters"""
    if not isinstance(self.api_key, str):
      print('api_key has to be a string: "Yourtopsecretkey123" ')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info('image size: {} x {} px'.format(im_width, im_height))

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logger.info('Connection test passed')
    else:
      raise Exception('Network could not be reached :/')

    # Set some parameters for formatting todos
    line_spacing = 1
    line_height = self.font.getsize('hg')[1] + line_spacing
    line_width = im_width
    max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [
      (0, spacing_top + _ * line_height ) for _ in range(max_lines)]

    # Get all projects by name and id
    all_projects = {project['id']: project['name']
                    for project in self._api.projects.all()}

    # Check if project from filter could be found
    if self.project_filter:
      for project in self.project_filter:
        if project not in all_projects:
          print('Could not find a project named {}'.format(project))
          self.project_filter.remove(project)

    # function for extracting project names from tasks
    get_project_name = lambda task: (self._api.projects.get_data(
                                     task['project_id'])['project']['name'])

    # If the filter is empty, parse all tasks which are not yet done
    if self.project_filter:
      tasks = (task.data for task in self._api.state['items']
               if (task['checked'] == 0) and
               (get_project_name(task) in self.project_filter))

    # If filter is not empty, parse undone tasks in only those projects
    else:
      tasks = (task.data for task in self._api.state['items'] if
               (task['checked'] == 0))

    # Simplify the tasks for faster processing
    simplified = [
      {
        'name':task['content'],
        'due':task['due'],
        'priority':task['priority'],
        'project':all_projects[ task['project_id'] ]
      }
      for task in tasks]

    print('simplified',simplified)

    # Group tasks by project name
    grouped = []

    if self.project_filter:
      for project in self.project_filter:
        project_name = all_projects[project]
        grouped[ project_name ] = [
          task for task in simplified if task['project'] == project_name]
    else:
      for project in all_projects:
        project_name, project_todo = all_projects[project], {}
        project_todo[ project_name ] = [
          task for task in simplified if task['project'] == project_name]
        grouped.append(project_todo)

    print(f"grouped: {grouped}")
    # Print tasks sorted by groups
    for project in grouped:
      print('*', project)
      for task in tasks:
        print('• {} {}'.format(
          task['due']['string'] if task['due'] != None else '', task['name']))


##    # Write rss-feeds on image
##    for _ in range(len(filtered_feeds)):
##      write(im_black, line_positions[_], (line_width, line_height),
##            filtered_feeds[_], font = self.font, alignment= 'left')

    # return the images ready for the display
    return im_black, im_colour

if __name__ == '__main__':
  print('running {0} in standalone/debug mode'.format(filename))
