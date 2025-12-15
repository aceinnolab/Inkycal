"""
Inkycal Todoist Module
Copyright by aceinnolab
"""
import logging

import arrow
import json
import os
import time
from datetime import datetime

from typing import Callable, Iterable, TypeVar

from inkycal.modules.template import InkycalModule

from todoist_api_python.api import TodoistAPI
import requests.exceptions

from inkycal.utils.canvas import Canvas
from inkycal.utils.functions import internet_available

logger = logging.getLogger(__name__)

T = TypeVar("T")

class Todoist(InkycalModule):
    """Todoist api class
    parses todos from the todoist api.
    """

    name = "Todoist API - show your todos from todoist"

    requires = {
        'api_key': {
            "label": "Please enter your Todoist API-key",
        },
    }

    optional = {
        'project_filter': {
            "label": "Show Todos only from following project (separated by a comma). Leave empty to show " +
                     "todos from all projects",
        },
        'show_priority': {
            "label": "Show priority indicators for tasks (P1, P2, P3)",
            "default": True
        }
    }

    def __init__(self, config):
        """Initialize inkycal_rss module"""

        super().__init__(config)

        config = config['config']

        # Check if all required parameters are present
        for param in self.requires:
            if param not in config:
                raise Exception(f'config is missing {param}')

        # module specific parameters
        self.api_key = config['api_key']

        # if project filter is set, initialize it
        if config['project_filter'] and isinstance(config['project_filter'], str):
            self.project_filter = config['project_filter'].split(',')
        else:
            self.project_filter = config['project_filter']

        # Priority display option
        self.show_priority = config.get('show_priority', True)

        self._api = TodoistAPI(config['api_key'])

        # Cache file path for storing last successful response
        self.cache_file = os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'todoist_cache.json')
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def _validate(self):
        """Validate module-specific parameters"""
        if not isinstance(self.api_key, str):
            print('api_key has to be a string: "Yourtopsecretkey123" ')


    def _fetch_with_retry(
            self,
            fetch_func: Callable[[], Iterable[T]],
            *,
            max_retries: int = 3,
            retry_statuses: set[int] = {502, 503, 504},
    ) -> list[T]:
        """
        Fetch data with retry logic and exponential backoff.

        Retries on:
        - Connection errors
        - HTTP errors with retryable status codes

        Args:
            fetch_func: Callable returning an iterable of results.
            max_retries: Maximum number of attempts.
            retry_statuses: HTTP status codes that should trigger a retry.

        Returns:
            A list of fetched items.

        Raises:
            requests.exceptions.RequestException
            RuntimeError: If all retries are exhausted.
        """
        for attempt in range(1, max_retries + 1):
            try:
                return list(fetch_func())

            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response else None
                if status not in retry_statuses or attempt == max_retries:
                    raise

            except requests.exceptions.ConnectionError:
                if attempt == max_retries:
                    raise

            delay = 2 ** (attempt - 1)
            logger.warning(
                "API request failed (attempt %d/%d), retrying in %ds...",
                attempt,
                max_retries,
                delay,
            )
            time.sleep(delay)

        raise RuntimeError("Max retries exceeded")

    def _save_cache(self, projects, tasks):
        """Save API response to cache file"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'projects': [{'id': p.id, 'name': p.name} for p in projects],
                'tasks': [{
                    'content': t.content,
                    'project_id': t.project_id,
                    'priority': t.priority,
                    'due': {'date': str(t.due.date)} if t.due else None
                } for t in tasks]
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.debug("Saved Todoist data to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _load_cache(self):
        """Load cached API response"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return None

    def _create_error_image(self, im_size, error_msg=None, cached_data=None):
        """Create an error message image when API fails"""
        im_width, im_height = im_size
        canvas = Canvas(im_size=im_size, font=self.font, font_size=self.fontsize)

        # Display error message
        line_spacing = 1
        line_height = canvas.get_line_height() + line_spacing

        messages = []
        if error_msg:
            messages.append("Todoist temporarily unavailable")

        if cached_data and 'timestamp' in cached_data:
            timestamp = arrow.get(cached_data['timestamp']).format('D-MMM-YY HH:mm')
            messages.append(f"Showing cached data from:")
            messages.append(timestamp)
        else:
            messages.append("No cached data available")
            messages.append("Please check your connection")

        # Center the messages vertically
        total_height = len(messages) * line_height
        start_y = (im_height - total_height) // 2

        for i, msg in enumerate(messages):
            y_pos = start_y + (i * line_height)
            # First line in red (colour image), rest in black
            canvas.write(
                xy= (0, y_pos),
                box_size=(im_width, line_height),
                text=msg,
                colour="colour" if i == 0 else "black"
            )

        return canvas.image_black, canvas.image_colour

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.debug(f'Image size: {im_size}')

        canvas = Canvas(im_size=im_size, font=self.font, font_size=self.fontsize)

        # Check if internet is available
        if not internet_available():
            logger.error("Network not reachable. Trying to use cached data.")
            cached_data = self._load_cache()
            if cached_data:
                # Process cached data below
                all_projects = [type('Project', (), p) for p in cached_data['projects']]
                all_active_tasks = [type('Task', (), {
                    'content': t['content'],
                    'project_id': t['project_id'],
                    'priority': t['priority'],
                    'due': type('Due', (), {'date': t['due']['date']}) if t['due'] else None
                }) for t in cached_data['tasks']]
            else:
                return self._create_error_image(im_size, "Network error", None)
        else:
            logger.info('Connection test passed')

            # Try to fetch fresh data from API
            try:
                all_projects = self._fetch_with_retry(self._api.get_projects)[0] or []
                all_tasks_api = self._fetch_with_retry(self._api.get_tasks) or []
                all_active_tasks = []
                for task_list in all_tasks_api:
                    all_active_tasks.extend(task_list)
                 # Save to cache on successful fetch
                self._save_cache(all_projects, all_active_tasks)
            except Exception as e:
                logger.error(f"Failed to fetch Todoist data: {e}")
                # Try to use cached data
                cached_data = self._load_cache()
                if cached_data:
                    logger.info("Using cached Todoist data")
                    all_projects = [type('Project', (), p) for p in cached_data['projects']]
                    all_active_tasks = [type('Task', (), {
                        'content': t['content'],
                        'project_id': t['project_id'],
                        'priority': t['priority'],
                        'due': type('Due', (), {'date': t['due']['date']}) if t['due'] else None
                    }) for t in cached_data['tasks']]
                else:
                    # No cached data available, show error
                    return self._create_error_image(im_size, str(e), None)

        # Set some parameters for formatting todos
        line_spacing = 1
        line_height = canvas.get_line_height() + line_spacing
        max_lines = im_height // line_height

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

        # Process the fetched or cached data
        filtered_project_ids_and_names = {project.id: project.name for project in all_projects}

        logger.debug(f"all_projects: {all_projects}")

        # Filter entries in all_projects if filter was given
        if self.project_filter:
            filtered_projects = [project for project in all_projects if project.name in self.project_filter]
            filtered_project_ids_and_names = {project.id: project.name for project in filtered_projects}
            filtered_project_ids = [project for project in filtered_project_ids_and_names]
            logger.debug(f"filtered projects: {filtered_projects}")

            # If filter was activated and no project was found with that name,
            # raise an exception to avoid showing a blank image
            if not filtered_projects:
                logger.error('No project found from project filter!')
                logger.error('Please double check spellings in project_filter')
                raise Exception('No matching project found in filter. Please '
                                'double check spellings in project_filter or leave'
                                'empty')
            # filtered version of all active tasks
            all_active_tasks = [task for task in all_active_tasks if task.project_id in filtered_project_ids]

        # Simplify the tasks for faster processing
        simplified = []
        for task in all_active_tasks:
            # Format priority indicator using circle symbols
            priority_text = ""
            if self.show_priority and task.priority > 1:
                # Todoist uses reversed priority (4 = highest, 1 = lowest)
                if task.priority == 4:  # P1 - filled circle (red)
                    priority_text = "● "  # Filled circle for highest priority
                elif task.priority == 3:  # P2 - filled circle (black)
                    priority_text = "● "  # Filled circle for high priority
                elif task.priority == 2:  # P3 - empty circle (black)
                    priority_text = "○ "  # Empty circle for medium priority

            # Check if task is overdue
            # Parse date in local timezone to ensure correct comparison
            try:
                due_date = arrow.get(task.due.date, "YYYY-MM-DD").replace(tzinfo='local') if task.due else None
            except Exception as e:
                logger.warning(f"Could not parse due date of task: {task} with due date: {str(task.due)} reason: ", e)
                continue
            today = arrow.now('local').floor('day')
            is_overdue = due_date and due_date < today if due_date else False

            # Format due date display
            if due_date:
                if due_date.floor('day') == today:
                    due_display = "TODAY"
                else:
                    due_display = due_date.format("D-MMM-YY")
            else:
                due_display = ""

            simplified.append({
                'name': task.content,
                'due': due_display,
                'due_date': due_date,
                'is_overdue': is_overdue,
                'priority': task.priority,
                'priority_text': priority_text,
                'project': filtered_project_ids_and_names[task.project_id] if task.project_id in filtered_project_ids_and_names else None
            })

        logger.debug(f'simplified: {simplified}')

        project_lengths = []
        due_lengths = []
        priority_lengths = []

        for task in simplified:
            if task["project"]:
                project_lengths.append(int(canvas.get_text_width(task['project']) * 1.1))
            if task["due"]:
                due_lengths.append(int(canvas.get_text_width(task['due']) * 1.1))
            if task["priority_text"]:
                priority_lengths.append(int(canvas.get_text_width(task['priority_text']) * 1.1))

        # Get maximum width of project names for selected font
        project_offset = int(max(project_lengths)) if project_lengths else 0

        # Get maximum width of project dues for selected font
        due_offset = int(max(due_lengths)) if due_lengths else 0

        # Get maximum width of priority indicators
        priority_offset = int(max(priority_lengths)) if priority_lengths else 0

        # create a dict with names of filtered groups
        groups = {group_name:[] for group_name in filtered_project_ids_and_names.values()}
        for task in simplified:
            group_of_current_task = task["project"]
            if group_of_current_task in groups:
                groups[group_of_current_task].append(task)

        # Sort tasks within each project group by due date first, then priority
        for project_name in groups:
            groups[project_name].sort(
                key=lambda task: (
                    task['due_date'] is None,  # Tasks with dates come first
                    task['due_date'] if task['due_date'] else arrow.get('9999-12-31'),  # Sort by date
                    -task['priority']  # Then by priority (higher priority first)
                )
            )

        logger.debug(f"grouped: {groups}")

        # Add the parsed todos on the image
        cursor = 0
        for name, todos in groups.items():
            if todos:
                for todo in todos:
                    if cursor < max_lines:
                        line_x, line_y = line_positions[cursor]

                        if todo['project']:
                            # Add todos project name
                            canvas.write(
                                xy=line_positions[cursor],
                                box_size=(project_offset, line_height),
                                text= todo['project'],
                                colour="colour",
                                alignment='left'
                            )

                        # Add todos due if not empty
                        if todo['due']:
                            # Show overdue dates in red, normal dates in black
                            canvas.write(
                                xy=(line_x + project_offset, line_y),
                                box_size=(due_offset, line_height),
                                text= todo['due'],
                                colour="colour" if todo.get('is_overdue', False) else "black",
                                alignment='left'
                            )

                        # Add priority indicator if present
                        if todo['priority_text']:
                            # P1 (priority 4) in red, P2 and P3 in black
                            canvas.write(
                                xy=(line_x + project_offset + due_offset, line_y),
                                box_size=(priority_offset, line_height),
                                text=todo['priority_text'],
                                colour="colour" if todo['priority'] == 4 else "black",
                                alignment='left'
                            )
                        if todo['name']:
                            # Add todos name
                            canvas.write(
                                xy=(line_x + project_offset + due_offset + priority_offset, line_y),
                                box_size=(im_width - project_offset - due_offset - priority_offset, line_height),
                                text=todo['name'],
                                alignment='left'
                            )
                        cursor += 1
                    else:
                        logger.error('More todos than available lines')
                        break

        # return the images ready for the display
        return canvas.image_black, canvas.image_colour
