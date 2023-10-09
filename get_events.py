from __future__ import print_function

import datetime
import os.path
import json
import pandas as pd
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/drive']

# print(sys.argv[1])
# days = int(sys.argv[1])

def get_events(d = 7):
    """
    Gets events for the next d days from the Fellowship Hall calendar.

    Parameters
    ----------

    d int :
        an int of how many days into the future events should be pulled

    Returns
    -------

    List of str, list(list)
    """

    print(d)
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        # Get start and end dates for the query
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        end_day_time = (datetime.datetime.today() + datetime.timedelta(days = d)).isoformat()[:10]+"T23:59:59.99Z"
        end_date = end_day_time[:10]

        events_result = service.events().list(
            calendarId='bozemanfellowship@gmail.com', 
            timeMin=now,
            timeMax = end_day_time, 
#             maxResults=n, # in case you'd rather just get N events
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print('No upcoming events found.')
            return
            
        meetings = []
        for e in events:
            if 'location' in e:
                loc = e['location']
            else:
                loc = None
            meetings.append(
                {
                    'title': e['summary'],
                    'location': loc,
                    'start_time': datetime.datetime.strftime(datetime.datetime.strptime(e['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'), "%Y-%m-%d %I:%M %p") 
#                     'end_time': datetime.datetime.strftime(datetime.datetime.strptime(e['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'), "%Y-%m-%d %I:%M %p"), 
                }
            )
            
        df = pd.DataFrame(meetings)

        values = [df.columns.values.tolist()]
        values.extend(df.values.tolist())

        return([end_date, values])

        # Writes to csv        
        # df.to_csv(
        #     path_or_buf = f'events_ending_{end_date}.csv', 
        #     index = False)
        
        # Writes to json
#         with open(f'events_ending_{end_date}.json', 'w', encoding='utf-8') as f:
#             json.dump(meetings, f, ensure_ascii=False, indent=4)
        
    except HttpError as error:
        print('An error occurred: %s' % error)

