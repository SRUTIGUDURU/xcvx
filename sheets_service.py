from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import json
from typing import List, Dict, Any

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
QUESTIONNAIRE_RANGE = 'Questionnaire!A:F'
MESSAGES_RANGE = 'Messages!A:E'
GROUPS_RANGE = 'Groups!A:C'

class SheetsService:
    def __init__(self):
        self.creds = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    def _get_credentials(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def get_questionnaire_data(self) -> List[Dict[str, Any]]:
        result = self.sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=QUESTIONNAIRE_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        return [dict(zip(headers, row)) for row in values[1:]]

    def save_questionnaire(self, data: Dict[str, Any]):
        values = [[
            data['email'],
            data['hobbies'],
            data['topics'],
            data['gender'],
            data['year'],
            data['purpose']
        ]]
        
        body = {
            'values': values
        }
        
        self.sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=QUESTIONNAIRE_RANGE,
            valueInputOption='RAW',
            body=body
        ).execute()

    def get_messages(self, group_name: str) -> List[Dict[str, Any]]:
        result = self.sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=MESSAGES_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        messages = [dict(zip(headers, row)) for row in values[1:]]
        return [msg for msg in messages if msg['group_name'] == group_name]

    def save_message(self, data: Dict[str, Any]):
        values = [[
            data['id'],
            data['group_name'],
            data['email'],
            data['message'],
            data['timestamp']
        ]]
        
        body = {
            'values': values
        }
        
        self.sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=MESSAGES_RANGE,
            valueInputOption='RAW',
            body=body
        ).execute()

    def get_groups(self) -> List[Dict[str, Any]]:
        result = self.sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=GROUPS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        return [dict(zip(headers, row)) for row in values[1:]]

    def save_groups(self, groups: List[Dict[str, Any]]):
        values = [[
            group['id'],
            group['group_name'],
            group['email']
        ] for group in groups]
        
        body = {
            'values': values
        }
        
        self.sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=GROUPS_RANGE,
            valueInputOption='RAW',
            body=body
        ).execute() 