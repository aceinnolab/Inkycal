#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inky-Calendar custom-functions for ease-of-use

Copyright by aceisace
"""

import time

def get_system_tz():
    """
    Gets the system-timezone

    Gets the timezone set by the system.

    Returns:
        - A timezone if a system timezone was found.
        - None if no timezone was found.

    The extracted timezone can be used to show the local time instead of UTC. e.g.

        >>> import arrow
        >>> print(arrow.now()) # returns non-timezone-aware time
        >>> print(arrow.now(tz=get_system_tz()) # prints timezone aware time.
    """
    try:
        local_tz = time.tzname[1]
    except:
        print('System timezone could not be parsed!')
        print('Please set timezone manually!. Setting timezone to None...')
        local_tz = None
    return local_tz