import json
from flask import jsonify, render_template, request
import logging
from traceback import format_exc

import src.shared.services.athlete_data_controller as athlete_data_controller
import src.shared.services.routes_data_controller as routes_data_controller
# Initialize logger
logger = logging.getLogger(__name__)

def athletes():
    """
    stats website
    """
    logger.info("athletes request received.")
    
    data = athlete_data_controller.load_athletes()

    return data

def years():
    """
    stats website
    """
    logger.info("athletes request received.")
    
    data = routes_data_controller.available_years()

    return jsonify(data)

