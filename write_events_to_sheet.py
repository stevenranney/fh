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

import json

import get_events

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/spreadsheets']

# d = int(sys.argv[1])

# Check if an argument was provided; if not, default to weekly
if len(sys.argv) == 1:
    t = 'weekly'
else:
    t = sys.argv[1]

def write_events_to_sheet(t = t):
    """
    Retrieves and writes events to a google sheet

    Parameters
    ----------

    d int :
        The date in the future through which the function will pull calendar events. 
        This date will also serve as the partial file name of the written sheet.
    
    Returns
    -------
    Satisfaction.

    """

    if t == 'weekly':
        d = 7
        spreadsheetId = '1zee2QgfDLStbDVuf-p9qYwDLdcsS2hj5_s48i2zrH58'
        # FH Weekly Calendar sheet ID - exists in the hall's workspace
        # spreadsheetId = '1ONrC2u1g1t4oSgSfQ_YvLf6fvq-hYi_jfriGWxmSuWc'
    elif t == 'daily':
        d = 1
        spreadsheetId = '1ONrC2u1g1t4oSgSfQ_YvLf6fvq-hYi_jfriGWxmSuWc'
    elif t is None: # reverts to weekly
        d = 7
        spreadsheetId = '1ONrC2u1g1t4oSgSfQ_YvLf6fvq-hYi_jfriGWxmSuWc'
    
    events = get_events.get_events(d)
    
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
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet = {
            'properties': {
                'title': 'FH Weekly Calendar'
            }
        }
        # Instantiate a spreadsheet
        # SHR: 10/10 not necessary because bradley created sheet
        # he wants me to use
        # spreadsheet = (
        #     service.
        #     spreadsheets().
        #     create(
        #         body=spreadsheet,
        #         fields='spreadsheetId'
        #         ).
        #     execute()
        # )

        # Insert spreadsheet ID here:
        # spreadsheetId = '1zee2QgfDLStbDVuf-p9qYwDLdcsS2hj5_s48i2zrH58'
        # FH Weekly Calendar sheet ID - exists in the hall's workspace
        #spreadsheetId = '1ONrC2u1g1t4oSgSfQ_YvLf6fvq-hYi_jfriGWxmSuWc'

        # Create data to go into spreadsheet
        sheet_information = {
        'valueInputOption': 'RAW',
            "data": [
                {'range': "Sheet1!A:C", 
                 'values': events[1]}
                ]
        }

        # make the request of the spreadsheet to add data
        request = (
            service.
            spreadsheets().
            values().
            batchUpdate(
                spreadsheetId = spreadsheetId, #spreadsheet.get('spreadsheetId'),
                body = sheet_information
            )
        )

        # EXECUTE REQUEST
        response = request.execute()

        print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
        return spreadsheet.get('spreadsheetId')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == '__main__':
    write_events_to_sheet(t)