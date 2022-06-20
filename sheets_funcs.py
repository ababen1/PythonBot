from __future__ import print_function
from array import array
import enum
from attr import field
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from setup import creds

SPREADSHEET_ID = '13zCT1ubfOCAejVlr5UwQNSp1XK3v3aiSopWkxjVLJp0'
PERSONAL_SPREEDSHEET_ID = '1T4zoflM3u1fZ4mDryZXbQhEAxSJg7EbZk-674Fcb7bI'

users_data = {}

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
EMAIL_LIST_DATA = {
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
    for email in get_spreadsheet_data(EMAIL_LIST_DATA[field]):
        emails.append(email[1])
    return emails

def get_keywords(field: FIELD) -> array:
    keywords = []
    for keyword in get_spreadsheet_data(KEYWORDS_DATA[field]):
        if keyword:
            keywords.append(keyword[0])
    return keywords

def get_spreadsheet_data(spreadsheet_range: str, id=SPREADSHEET_ID):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=id,
                                    range=spreadsheet_range).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        else:
            return values

    except HttpError as err:
        print(err)

def get_user_data(email: str) -> dict:
    if not users_data:
        load_users_data()
    return users_data.get(email, None)

def load_users_data():
    range = 'Form Responses 1!B2:H100'
    data = get_spreadsheet_data(range, PERSONAL_SPREEDSHEET_ID)
    for value in data:
        users_data[value[2]] = {
            "name": value[0],
            "field": hebrew_to_field(value[1]),
            "blacklist": value[4],
            "keywords": value[5],
            "send_email": ('מייל' in value[6]),
            "send_whatsapp": ('ווטספ' in value[6])
        }

def hebrew_to_field(hebrew_str: str) -> FIELD:
    # Converts hebrew string to a field type
    switcher = {
        "תכנות": FIELD.TECH,
        "עיצוב גרפי": FIELD.DESIGN,
        "שיווק": FIELD.SOCIAL,
        "פרוייקטים לסטודיו": FIELD.ENTER_STUDIO}
    return switcher.get(hebrew_str, None)
