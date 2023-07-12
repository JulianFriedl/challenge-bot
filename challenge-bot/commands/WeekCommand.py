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
    "AlpineSki": 120, # Skifahren
    "RockClimbing": 60, # Bouldern/Klettern
    "Workout": 60, # HIT Workout 2 HIT in der Woche = 1 Punkt
    "Snowshoe": 60,
    "VirtualRide" : 60
}

# Set up a variable to store the number of points required
POINTS_REQUIRED = 3

# Set up a variable to store the number of HIT workouts required
HIT_REQUIRED = 2
HIT_MIN_TIME = 10

# tolorance for time required in minutes, for example if set to 1 will give points to activity "Run" duration: 29 min
SPAZI = 3

# Set a limit for the number of Walking activities count in a week
WALKING_LIMIT = 2




def getWhoNeedsToPay(week) -> str:
    
    loaded_creds = AuthDataController.load_credentials()
    if loaded_creds == None:
        return ('There are no authenticate Athletes, please use the !strava_auth command.')
        # Calculate the start and end dates of the week
    year = datetime.date.today().year # Get the current year
    start_date = datetime.date.fromisocalendar(year, week, 1) # Get the first day of the week
    end_date = datetime.date.fromisocalendar(year, week, 7) # Get the last day of the week

    # Get the current date as a date object
    current_date = datetime.date.today()
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

            # Get the data for this athlete from the api response
            data = response.json()

            # Get the number of points for this athlete from the data
            points = get_points(data, week)

            # Check if the number of points is less than the points required if, before week 9 only two points were required
            if points < (POINTS_REQUIRED if week > 9 else 2):
                # This athlete needs to pay
                return_string += f"{username} needs to pay because they only earned {points} point/s.\n"
            else:
                # This athlete does not need to pay
                return_string += f"{username} does not need to pay because they earned {points} point/s.\n"


        else:
            # Handle unsuccessful response
            return_string += f"Error: Could not get activities for {username}. Status code: {response.status_code}\n"





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
        
        # Convert the activity date string to a date object
        activity_date = datetime.datetime.strptime(activity_date_str, "%Y-%m-%d")
        # Get the week number of the activity date as an integer
        activity_week = activity_date.isocalendar()[1]
        
        # Check if the week number is equal to the week number parameter
        if activity_week == week:
            # The activity is in the given week, so we can check it against the rules
            # Check if the activity type is HIT Workout
            if activity_type == "Workout" and activity_duration < (60-SPAZI) and activity_duration > HIT_MIN_TIME:
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

                    # Count the number of walks in the activities_done set
                    walk_count = len([a for a in activities_done if a[0] == "Walk"])
                    if walk_count >= 2 and activity_type == "Walk": # Only 2 walks per week are allowed
                        print("No points for Walk because only 2 walks allowed")
                        continue
                    
                    # Create a set of dates from the activities_done set
                    dates_done = {a[1] for a in activities_done}
                    # Check if a point has already been awarded for an activity today
                    # TODO Potential Bug here when with multiple activities and one the spans multiple days, not sure though might look into later
                    if activity_date not in dates_done:
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

                        # Calculate the number of days that the activity spans, only if the activity goes past midnight by the min_duration amount
                        days = end_ordinal - start_ordinal + 1
                        
                        # Calculate the time in minutes that has passed from midnight to end_date
                        elapsed_time_past_midnight_min = end_date.hour * 60 + end_date.minute

                        #TODO think of a good threshold for adding multiple points for an activity
                        if elapsed_time_past_midnight_min < min_duration and days > 1:
                            print(f"Not added {days} points because elapsed_time_past_midnight_min: {elapsed_time_past_midnight_min} which is under the treshold")
                            days -= 1

                        # Add one point for each day that the activity spans
                        points += days

                        # Add this activity type and date to the set of activities done
                        activities_done.add((activity_type, activity_date))

                        # Print out a message for debugging
                        print(f"Added {days} point/s for {activity_type} on {activity_date}")


    # Return the number of points earned
    return points
