import commands.WeekCommand as WeekCommand
import commands.StravaAuthCommand as StravaAuth
import commands.TotalCommand as TotalCommand

def handle_response(message) -> str:
    p_message = str(message.lower())
    
    if p_message.startswith('!week'):
        is_valid, week = parse_week_input(message)
        if is_valid:
            return WeekCommand.getWhoNeedsToPay(week)
        else:
            return 'Invalid Parameter!\nMake sure command is of type:\n("!week <Nr>", Nr...A Number indicating the calender week in range(1,52))'
        r
    elif p_message == '!total':
        return TotalCommand.getYearlyPayments()
    elif p_message == '!strava_auth':
        return StravaAuth.stravaAuth()
    elif p_message == '!help':
        return 'Command: !week\n    Parameter: Week:int in range(1,52)\n    Returns the people who need to pay in the specified calender week\nCommand: !total\n    Parameter: none\n    Returns the total amount of money each participant has to pay.'
    return ''

def parse_week_input(message):
    parts = message.split()
    if len(parts) != 2:
        return (False, None)
    command, week_str = parts
    if command != "!week":
        return (False, None)
    try:
        week = int(week_str)
    except ValueError:
        return (False, None)
    if not 1 <= week <= 52:
        return (False, None)
    return (True, week)