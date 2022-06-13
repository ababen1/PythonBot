from __future__ import print_function
from array import array
from ast import keyword
import enum
import imp

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pyparsing import Keyword
from setup import creds

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

def get_groups(field: FIELD) -> array:
    groups = []
    for group in get_spreadsheet_data(GROUPS_DATA[field]):
        groups.append(group[0])
    return groups

def get_emails(field: FIELD) -> array:
    if field == FIELD.ENTER_STUDIO:
        return ["livne@s-tov.org.il"]
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