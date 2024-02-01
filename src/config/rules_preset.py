"""
file: constants.py

description: This module contains all the constants that are used by the bot commands.

Author: Julian Friedl
"""
CHALLENGE_START_WEEK = 1
PRICE_PER_WEEK = 5
RULES = {
        "Ride": 60,
        "Run": 30,
        "WeightTraining": 60,
        "NordicSki": 60,
        "BackcountrySki": 60,
        "Hike": 60,
        "Walk": 60,
        "Swim": 30,
        "AlpineSki": 120,
        "RockClimbing": 60,
        "Workout": 60, #Hit workout, Teamsportarten die nicht auf Strava sind
        "Snowshoe": 60,
        "VirtualRide": 60,
        "Kayaking": 60
}
POINTS_REQUIRED = 3
JOKER = 1
SPAZI = 3 # tolerance in min
WALKING_LIMIT = 1 # maximum amount of points you can get from walking in a week
HIT_REQUIRED = 2 # Required hit workouts for one point
HIT_MIN_TIME = 10 # min time for a hit workout
MIN_DURATION_MULTI_DAY = 360 # min duration you have to pass over midnight in order for a multiday activity to give you an extra point