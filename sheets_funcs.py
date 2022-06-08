from __future__ import print_function
from array import array
from ast import keyword
import enum
from multiprocessing.dummy import Array 

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pyparsing import Keyword

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = '13zCT1ubfOCAejVlr5UwQNSp1XK3v3aiSopWkxjVLJp0'
SAMPLE_RANGE_NAME = 'קבוצות מציאת עבודה - הייטק!A4:A'

class FIELD(enum.Enum):
    TECH = 1
    DESIGN = 2
    SOCIAL = 3
    ENTER_STUDIO = 4

GROUPS_DATA = {
    FIELD.TECH: "קבוצות מציאת עבודה - הייטק!A4:A",
    FIELD.DESIGN: "קבוצות מציאת עובדה - מעצבים!A4:A",
    FIELD.SOCIAL: "קבוצות מציאת עבודה - סושיאל!A4:A",
    FIELD.ENTER_STUDIO: "קבוצות מציאת פרוייקטים!A4:A"
    }
USERS_DATA = {
    FIELD.TECH: "רשומים למציאת עבודה - מתכנתים!A2:B",
    FIELD.DESIGN: "רשומים למציאת עבודה - מעצבים!A2:B",
    FIELD.SOCIAL: "רשומים למציאת עבודה - סושיאל ושיווק!A2:B",
    FIELD.ENTER_STUDIO: ""
    }
KEYWORDS_DATA = {
    FIELD.TECH: "מילות מפתח!B2:B",
    FIELD.DESIGN: "מילות מפתח!C2:C",
    FIELD.SOCIAL: "מילות מפתח!D2:D",
    FIELD.ENTER_STUDIO: "מילות מפתח!A2:A"
    }


def _search_for_credentials() -> dict:
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
    return creds

def get_groups(field: FIELD) -> array:
    groups = []
    for group in get_spreadsheet_data(GROUPS_DATA[field]):
        groups.append(group[0])
    return groups

def get_emails(field: FIELD) -> array:
    emails = []
    for email in get_spreadsheet_data(USERS_DATA[field]):
        emails.append(email[1])
    return emails

def get_keywords(field: FIELD) -> array:
    keywords = []
    for keyword in get_spreadsheet_data(KEYWORDS_DATA[field]):
        if keyword:
            keywords.append(keyword[0])
    return keywords

def get_spreadsheet_data(spreadsheet_range: str):
    creds = _search_for_credentials()
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=spreadsheet_range).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        else:
            return values

    except HttpError as err:
        print(err)