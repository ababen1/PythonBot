from __future__ import print_function
from array import array

import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from setup import creds

def gmail_send_message(recipents: array, content: str, subject: str, html: bool = True):
    """Create and insert a draft email.
       Print the returned draft's message and id.
       Returns: Draft object, including draft id and message meta data.

      Load pre-authorized user credentials from the environment.
      TODO(developer) - See https://developers.google.com/identity
      for guides on implementing OAuth2 for the application.
    """
    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)
        mime_message  = EmailMessage()

        # headers
        mime_message ['To'] = recipents
        mime_message ['Subject'] = subject
       
       # text
        mime_message.set_content(content, "html" if html else "plain")

       

        # encoded message
        encoded_message = base64.urlsafe_b64encode(mime_message .as_bytes()).decode()

        create_message = {
                'raw': encoded_message,
                
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message
