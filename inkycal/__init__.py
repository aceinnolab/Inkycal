"""Inkycal package bootstrap."""

from inkycal.loggers import configure_logging
from inkycal.utils.ssl import configure_ssl_context

configure_logging()
configure_ssl_context()
