# Commands

The following commands are available for the bot:
- `/help`: Displays every command and how to use it.
- `/strava_auth`: Sends a link to the Strava authorization page, where you can grant permission for the bot to access your data. And exchanges the authorization code for an access token and stores it for future requests. 
- `/week <Nr>:` This command requires a calendar week number as a parameter. When invoked, the bot performs several actions to provide data for the specified week:
    1. The bot checks if there are any registered athletes. If not, it notifies the user that there are no authenticated athletes and they should use the !strava_auth command.
    2. The bot validates if the requested week is not in the future. If the week is invalid, it returns an error.
    3. For each registered athlete, the bot retrieves the athlete's activities for the specified week. It calculates the points earned by the athlete based on the duration and type of each activity (using rules defined in the Activity class).
    4. The bot also counts the number of High-Intensity Training (HIT) workouts, with each pair of HIT workouts counting as an additional point. An activity must last at least 10 minutes but less than 60 minutes to be considered as a HIT workout.
    5. If an athlete performs a multi-day activity that lasts more than 6 hours past midnight, they earn an additional point for each day.
    6. If the total points earned by the athlete is less than 3 (or 2 if the week number is less than 9), the bot states that the athlete needs to pay. If the points are equal to or greater than the threshold, the bot states that the athlete does not need to pay.
    7. The command returns a Discord embed message with the payment details for each athlete for the week.
- `/total`: Returns all challenge members and the amount they have to pay.
    1. Retrieves all registered athlete's activity data for a specified year from the Strava API.
    2. Checks if the same rules from the week command apply for each Week in the retrieved year
    3. Returns a Discord embed containing each athlete's annual payment information. The annual payment is calculated based on the number of weeks an athlete didn't meet the required activity points.