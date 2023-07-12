import commands.WeekCommand as WeekCommand
import datetime
import time
import AuthDataController
import requests
import json
import AuthRefresh

CHALLENGE_START_WEEK = 9
def getYearlyPayments() -> str:

    # Get the current date as a date object
    current_date = datetime.date.today()

    # Get the current year as an integer
    current_year = current_date.year

    # Set up a variable to store the price per week
    PRICE_PER_WEEK = 5

    # Set up a dictionary to store the amounts for each athlete
    amounts = {}

    # Get the current week number as an integer
    current_week = datetime.date.today().isocalendar()[1]

    # Get the start and end dates of the year as date objects
    start_date = datetime.date(current_year, 1, 1)
    end_date = datetime.date(current_year, 12, 31)

    # Convert the start and end dates to seconds since Unix epoch
    start_date_seconds = time.mktime(start_date.timetuple()) # Option 1: remove datetime.fromisoformat()
    end_date_seconds = time.mktime(end_date.timetuple())

    # Load the credentials from the file
    loaded_creds = AuthDataController.load_credentials()

    # Check if there are any authenticated athletes
    if loaded_creds == None:
        return ('There are no authenticate Athletes, please use the !strava_auth command.')

    # Loop through the credentials and get the activities for each athlete
    for cred in loaded_creds:
        # Refresh the token if needed and update the credential dictionary
        cred = AuthRefresh.refresh_token(cred)
        # Save the updated credential to the file
        AuthDataController.save_credentials(json.dumps(cred))
        username = cred["athlete"]["username"]
        access_token = cred["access_token"]
        
       # Set up a variable to store the list of activities
        activities = []

        # Set up a variable to store the current page number
        page = 1

        # Set up a variable to store the maximum number of activities per page
        per_page = 30

        # Set up a variable to store the flag for reaching the end of the results
        end_of_results = False

        # Loop until the end of the results is reached or the end date is exceeded
        while not end_of_results:
            # Set up the headers and params for the api call
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {"before": end_date_seconds, "after": start_date_seconds, "page": page, "per_page": per_page}

            # Make the api call to get the current page of activities for this athlete in this year
            response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=params)

            # Check if the response is successful
            if response.status_code == 200:
                # Parse the response data as a list of dictionaries
                data = response.json()

                # Check if the data is empty
                if not data:
                    # The data is empty, so we have reached the end of the results
                    end_of_results = True
                else:
                    # The data is not empty, so we can append it to the activities list
                    activities.extend(data)

                    # Increment the page number by one
                    page += 1

                    # Check if any of the activities have a date that exceeds the end date
                    for activity in data:
                        # Get the activity date string from the dictionary
                        activity_date_str = activity["start_date_local"][:10] # Get only the YYYY-MM-DD part

                        # Convert the activity date string to a date object
                        activity_date = datetime.date.fromisoformat(activity_date_str)

                        # Compare the activity date with the end date
                        if activity_date > end_date:
                            # The activity date exceeds the end date, so we have reached the end of the results
                            end_of_results = True
                            break

            elif response.status_code == 429:
               return "Strava Rate Limit exceeded, wait 15 min until you can try again."
 
            else:
                # The response is unsuccessful for some other reason, so we handle it accordingly

                # Print out an error message for debugging
                return f"Error: Could not get activities for {username}. Status code: {response.status_code}"

           
    amount_to_pay = 0
    # Loop through the weeks from CHALLENGE_START_WEEK to the current week number
    for week in range(CHALLENGE_START_WEEK, current_week):
         # Get the number of points for this athlete from the data and the week number
        if WeekCommand.get_points(activities, week) < WeekCommand.POINTS_REQUIRED:
            print(f"Pay in Week: {week}")
            amount_to_pay += PRICE_PER_WEEK
        # Store the points in the amounts dictionary
        amounts[username] = amount_to_pay


    # Set up a variable to store the return string
    return_string = ""

    # Loop through the amounts dictionary and format the return string with the results
    for username, amount in amounts.items():
        if amount > 0:
            # This athlete needs to pay
            return_string += f"{username} needs to pay {amount} euros for {current_year}.\n"
        else:
            # This athlete does not need to pay
            return_string += f"{username} does not need to pay for {current_year}.\n"

    # Return the return string
    return return_string
