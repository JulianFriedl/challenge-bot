import json
from flask import jsonify, render_template, request
import logging
from traceback import format_exc

import src.shared.services.routes_data_controller as routes_data_controller
# Initialize logger
logger = logging.getLogger(__name__)

BLACKLIST_ACTIVITIES=[9525356360]

def map():
    """
    Return JSON of the map as specified
    """
    years = request.args.get('years')  # Get 'years' as a list
    athlete_ids = request.args.get('athletes')  # Get 'athlete_ids' as a list
    
    # Assuming 'load_routes' can accept a list of years and return data accordingly
    data = routes_data_controller.load_routes(years)

    
    logger.info("map request received")
    filtered_data = {}
    for year, year_data in data.items():
        if year_data:  # Check if year_data is not an empty dict
            # Filter athletes based on provided athlete_ids
            filtered_athletes = {
                k: v for k, v in year_data.get('athletes', {}).items() if str(v['user_id']) in athlete_ids
            }

            # Further filter the routes to remove any that are in the blacklist
            for athlete_id, athlete_data in filtered_athletes.items():
                athlete_data['routes'] = [
                    route for route in athlete_data.get('routes', [])
                    if route.get('activity_id') not in BLACKLIST_ACTIVITIES
                ]
            
            if filtered_athletes:
                filtered_data[year] = {'athletes': filtered_athletes}
    
    
    return jsonify(filtered_data)

