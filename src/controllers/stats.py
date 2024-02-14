from flask import request
import logging
from traceback import format_exc

# Initialize logger
logger = logging.getLogger(__name__)

def stats():
    """
    stats website
    """
    logger.info("Stats request received.")
