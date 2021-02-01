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

class Todoist(inkycal_module):
  """Todoist api class
  parses todo's from api-key
  """

  name = "Todoist API - show your todos from todoist"

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
        raise Exception(f'config is missing {param}')

    # module specific parameters
    self.api_key = config['api_key']

    # if project filter is set, initialize it
    if config['project_filter'] and isinstance(config['project_filter'], str):
      self.project_filter = config['project_filter'].split(',')
    else:
      self.project_filter = config['project_filter']

    self._api = todoist.TodoistAPI(config['api_key'])
    self._api.sync()

    # give an OK message
    print(f'{filename} loaded')

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
    logger.info(f'Image size: {im_size}')

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logger.info('Connection test passed')
      self._api.sync()
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

    logger.debug(f"all_projects: {all_projects}")

    # Filter entries in all_projects if filter was given
    if self.project_filter:
      for project_id in list(all_projects):
        if all_projects[project_id] not in self.project_filter:
          del all_projects[project_id]

      logger.debug(f"all_project: {all_projects}")

      # If filter was activated and no roject was found with that name,
      # raise an exception to avoid showing a blank image
      if all_projects == {}:
        logger.error('No project found from project filter!')
        logger.error('Please double check spellings in project_filter')
        raise Exception('No matching project found in filter. Please '
                        'double check spellings in project_filter or leave'
                        'empty')

    # Create single-use generator to filter undone and non-deleted tasks
    tasks = (task.data for task in self._api.state['items'] if
               task['checked'] == 0 and task['is_deleted']==0)

    # Simplify the tasks for faster processing
    simplified = [
      {
        'name':task['content'],
        'due':task['due']['string'] if task['due'] != None else "",
        'priority':task['priority'],
        'project':all_projects[ task['project_id'] ]
      }
      for task in tasks]

    # logger.debug(f'simplified: {simplified}')

    # Get maximum width of project names for selected font
    project_width = int(max([
      self.font.getsize(task['project'])[0] for task in simplified ]) * 1.1)

    # Get maximum width of project dues for selected font
    due_width = int(max([
      self.font.getsize(task['due'])[0] for task in simplified ]) * 1.1)

    # Group tasks by project name
    grouped = {name: [] for  id_, name in all_projects.items()}

    for task in simplified:
      if task['project'] in grouped:
        grouped[task['project']].append(task)

    logger.debug(f"grouped: {grouped}")


    # Add the parsed todos on the image
    cursor = 0
    for name, todos in grouped.items():
      if todos != []:
        for todo in todos:
          line_x, line_y = line_positions[cursor]

          # Add todo project name
          write(
            im_colour, line_positions[cursor],
            (project_width, line_height),
            todo['project'], font=self.font, alignment='left')

          # Add todo due if not empty
          if todo['due'] != "":
            write(
              im_black,
              (line_x + project_width, line_y),
              (due_width, line_height),
              todo['due'], font=self.font, alignment='left')

          # Add todo name
          write(
            im_black,
            (line_x+project_width+due_width, line_y),
            (im_width-project_width-due_width, line_height),
            todo['name'], font=self.font, alignment='left')

          cursor += 1
          if cursor > max_lines:
            logger.error('More todos than available lines')
            break

    # return the images ready for the display
    return im_black, im_colour

if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
