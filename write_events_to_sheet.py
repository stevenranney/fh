import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

import sys

import get_events

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/spreadsheets']

d = sys.argv[1]

def write_events_to_sheet(d = d):
    """
    Retrieves and writes events to a google sheet

    Parameters
    ----------

    d int :
        The date in the future through which the function will pull calendar events. 
        This date will also serve as the file name of the written sheet.
    
    Returns
    -------
    Satisfaction.

    """

    events = get_events(d)
    
    if events[0] is not None:
        print(f"got {d} days' worth of events! yay!")
    else: 
        print('no events retrieved. Sad face.')

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

    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet = {
            'properties': {
                'title': f'events_through_{events[0]}'
            }
        }
        # Instantiate a spreadsheet
        spreadsheet = (
            service.
            spreadsheets().
            create(
                body=spreadsheet,
                fields='spreadsheetId'
                ).
            execute()
        )

        # Create data to go into spreadsheet
        batch_update_values_request_body = {
        'value_input_option': 'RAW',
        'data': events[1] }

        # make the request of the spreadsheet to add data
        request = (
            service.
            spreadsheets().
            values().
            batchUpdate(
                spreadsheetId=spreadsheet.get('spreadsheetId'),
                body=batch_update_values_request_body
            )
        )

        # EXECUTE REQUEST
        response = request.execute()

        print(spreadsheet.get('spreadsheetId'))
        # print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
        return spreadsheet.get('spreadsheetId')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


# if __name__ == '__main__':
#     # Pass: title
#     create(t)