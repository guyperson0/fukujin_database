import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# https://developers.google.com/workspace/sheets/api/quickstart/python

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class LoadSheet:
    def __init__(self, spreadsheet_id, sheet_name, sheet_range):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.sheet_range = sheet_range

    def get_creds(self):

        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("sheets_token.json"):
            creds = Credentials.from_authorized_user_file("sheets_token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("sheets_token.json", "w") as token:
                token.write(creds.to_json())

        return creds
    
    def load_sheet(self, majorDimension="ROWS"):
        service = build("sheets", "v4", credentials=self.get_creds())

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=f"'{self.sheet_name}'!{self.sheet_range}", majorDimension=majorDimension)
            .execute()
        )

        if not result:
            raise Exception("No data!!!")
        
        return result.get("values")