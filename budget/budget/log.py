from os import environ
import logging
from logzero import setup_logger

# https://docs.python.org/3/library/logging.html#logging-levels
loglevel: int = logging.WARNING  # (30)
if "MINT_LOGS" in environ:
    loglevel = int(environ["MINT_LOGS"])

# logzero handles this fine, can be imported/configured
# multiple times
logger = setup_logger(name="budget", level=loglevel)
