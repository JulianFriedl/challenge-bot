import AuthDataController
import json
import requests
import datetime
import time
import AuthRefresh

# Set up a dictionary to store the rules
RULES = {
    "Ride": 60, # Radlfohrn
    "Run": 30, # Laufen
    "WeightTraining": 60, # Gym
    "NordicSki": 60, # Langlaufen
    "BackcountrySki": 0, # Skitour
    "Hike": 60, # Wandern
    "Walk": 60, # Spazieren
    "Swim": 30, # Schwimmen
    "TeamSports": 60, # Volleyball/Basketball/Fußball
    "AlpineSki": 120, # Skifahren
    "RockClimbing": 60, # Bouldern/Klettern
    "Workout": 0 # HIT Workout 2 HIT in der Woche = 1 Punkt
}

# Set up a variable to store the number of points required
POINTS_REQUIRED = 3

# Set up a variable to store the number of HIT workouts required
HIT_REQUIRED = 2

# tolorance for time required in minutes, for example if set to 1 will give points to activity "Run" duration: 29 min
SPAZI = 0


def getWhoNeedsToPay(week) -> str:
    
    loaded_creds = AuthDataController.load_credentials()
    #print(json.dumps(loaded_creds))
    if loaded_creds == None:
        return ('There are no authenticate Athletes, please use the !strava_auth command.')
        # Calculate the start and end dates of the week
    year = datetime.date.today().year # Get the current year
    start_date = datetime.date.fromisocalendar(year, week, 1) # Get the first day of the week
    end_date = datetime.date.fromisocalendar(year, week, 7) # Get the last day of the week

    # Get the current date as a date object
    current_date = datetime.date.today()
    # Add one day to the start date to make it inclusive
    start_date += datetime.timedelta(days=1)
    # Add one day to the end date to make it inclusive
    end_date += datetime.timedelta(days=1)

        # Check if the end date exceeds the current date
    if end_date > current_date:
        # The end date exceeds the current date, so we return an error message and stop the function
        return f"Error: The entered date exceeds the current date. Please enter a valid week number."
    
    return_string = ""
    return_string += f"The system currently has {len(loaded_creds)} authenticated athlete/s!\n"
    return_string += f"Showing Results for Week {week}\n"


    # Convert the start and end dates to seconds since Unix epoch
    # Convert the start and end dates to seconds since Unix epoch
    start_date_seconds = time.mktime(start_date.timetuple()) # Option 1: remove datetime.fromisoformat()
    end_date_seconds = time.mktime(end_date.timetuple())


    # Set up a dictionary to store the activity counts for each athlete
    activity_counts = {}

    for cred in loaded_creds:
        # Refresh the token if needed and update the credential dictionary
        cred = AuthRefresh.refresh_token(cred)
        # Save the updated credential to the file
        AuthDataController.save_credentials(json.dumps(cred))
        username = cred["athlete"]["username"]
        access_token = cred["access_token"]

        # Set up the headers and params for the api call
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"before": end_date_seconds, "after": start_date_seconds}
        
        # Print out the headers and params for debugging
        #print(f"Headers: {headers}")
        #print(f"Params: {params}")

        # Make the api call to get the activities for this athlete
        response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=params)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the response data as a list of dictionaries
            data = response.json()
            # Print out the data for debugging
            # print(f"Data: {data}")
            # Count how many activities this athlete has done in this week
            count = len(data)

            # Store the count in the dictionary
            activity_counts[username] = count

        else:
            # Handle unsuccessful response
            return_string += f"Error: Could not get activities for {username}. Status code: {response.status_code}\n"


    # Loop through the activity counts and determine who needs to pay
    for username, count in activity_counts.items():
        # Get the data for this athlete from the api response
        data = response.json()

        # Get the number of points for this athlete from the data
        points = get_points(data, week)

        # Check if the number of points is less than the points required
        if points < POINTS_REQUIRED:
            # This athlete needs to pay
            return_string += f"{username} needs to pay because they only earned {points} point/s.\n"
        else:
            # This athlete does not need to pay
            return_string += f"{username} does not need to pay because they earned {points} point/s.\n"


    return return_string

def get_points(data, week):
    # Set up a variable to store the number of points earned
    points = 0

    # Set up a set to store the activities done in each day
    activities_done = set()

    # Set up a counter to store the number of HIT workouts done in that week
    hit_count = 0

    # Loop through the data as a list of dictionaries
    for activity in data:
        # Get the activity type, duration and date from the dictionary
        activity_type = activity["type"]
        activity_duration = activity["elapsed_time"] / 60 # Convert seconds to minutes
        activity_date_str = activity["start_date_local"][:10] # Get only the YYYY-MM-DD part
        
        print(activity_date_str)
        # Convert the activity date string to a date object
        activity_date = datetime.datetime.strptime(activity_date_str, "%Y-%m-%d")
        # Get the week number of the activity date as an integer
        activity_week = activity_date.isocalendar()[1]

        # Check if the week number is equal to the week number parameter
        if activity_week == week:
            # The activity is in the given week, so we can check it against the rules
            # Check if the activity type is HIT Workout
            if activity_type == "Workout":
                # Add one to the hit counter for this activity
                hit_count += 1

                # Print out a message for debugging
                print(f"Added one HIT Workout on {activity_date}")

                # Check if the hit counter has reached the hit required value
                if hit_count == HIT_REQUIRED:
                    # The hit counter has reached the hit required value, so we can add one point

                    # Add one point for this activity
                    points += 1

                    # Reset the hit counter to zero
                    hit_count = 0

                    # Print out a message for debugging
                    print(f"Added one point for {HIT_REQUIRED} HIT Workouts")
            # Check if the activity type is in the rules dictionary
            elif activity_type in RULES:
                # Get the minimum duration for this activity type from the rules dictionary
                min_duration = RULES[activity_type]

                # Check if the activity duration is equal or greater than the minimum duration
                if activity_duration >= min_duration-SPAZI:
                    # Check if this activity type has already been done in this day
                    # TODO Potential Bug here when with multiple activities and one the spans multiple days, not sure though might look into later
                    if (activity_type, activity_date) not in activities_done:
                        # This activity type has not been done in this day, so we can count it

                        # Get the start date and elapsed time of the activity as strings
                        start_date_str = activity["start_date_local"]
                        elapsed_time_str = activity["elapsed_time"]

                        
                        # Convert the start date string to a datetime object
                        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%SZ")

                        # Convert the elapsed time string to a timedelta object
                        elapsed_time = datetime.timedelta(seconds=int(elapsed_time_str))

                        # Calculate the end date by adding the elapsed time to the start date because the end date isn't a required field in the api
                        end_date = start_date + elapsed_time

                        # Get the ordinal numbers of the start and end dates
                        start_ordinal = start_date.toordinal()
                        end_ordinal = end_date.toordinal()

                        # Calculate the number of days that the activity spans
                        days = end_ordinal - start_ordinal + 1

                        # Add one point for each day that the activity spans
                        points += days

                        # Add this activity type and date to the set of activities done
                        activities_done.add((activity_type, activity_date))

                        # Print out a message for debugging
                        print(f"Added {days} point/s for {activity_type} on {activity_date}")


    # Return the number of points earned
    return points
