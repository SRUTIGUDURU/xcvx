import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

def setup_google_sheets():
    """Set up Google Sheets API and create necessary sheets"""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # Load environment variables
    load_dotenv()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    if not spreadsheet_id:
        print("Error: SPREADSHEET_ID not found in .env file")
        return False
    
    # Get credentials
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found. Please download it from Google Cloud Console")
                return False
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Create service
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Define sheet headers
    questionnaire_headers = [['email', 'hobbies', 'topics', 'gender', 'year', 'purpose']]
    messages_headers = [['id', 'group_name', 'email', 'message', 'timestamp']]
    groups_headers = [['id', 'group_name', 'email']]
    
    # Create sheets if they don't exist
    try:
        # Create Questionnaire sheet
        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range='Questionnaire!A1',
            valueInputOption='RAW',
            body={'values': questionnaire_headers}
        ).execute()
        print("Created Questionnaire sheet")
        
        # Create Messages sheet
        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range='Messages!A1',
            valueInputOption='RAW',
            body={'values': messages_headers}
        ).execute()
        print("Created Messages sheet")
        
        # Create Groups sheet
        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range='Groups!A1',
            valueInputOption='RAW',
            body={'values': groups_headers}
        ).execute()
        print("Created Groups sheet")
        
        print("Google Sheets setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error setting up Google Sheets: {str(e)}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['static', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory} directory")

def main():
    print("Starting setup...")
    
    # Create directories
    create_directories()
    
    # Setup Google Sheets
    if setup_google_sheets():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Run the FastAPI server: uvicorn app:app --reload")
        print("2. Run the clustering script: python clustering.py")
        print("3. Open http://localhost:8000 in your browser")
    else:
        print("\nSetup failed. Please check the errors above and try again.")

if __name__ == "__main__":
    main() 