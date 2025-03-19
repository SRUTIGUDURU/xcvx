# Find-A-Friend

A web application that helps users find friends based on their interests and preferences using Google Sheets for data storage and Vercel for deployment.

## Setup Instructions

1. Create a Google Cloud Project and enable the Google Sheets API
2. Create a service account and download the credentials
3. Create a Google Sheet with three sheets:
   - Questionnaire (columns: email, hobbies, topics, gender, year, purpose)
   - Messages (columns: id, group_name, email, message, timestamp)
   - Groups (columns: id, group_name, email)
4. Share the Google Sheet with the service account email
5. Set up environment variables:
   - Create a `.env` file with:
     ```
     SPREADSHEET_ID=your_spreadsheet_id
     ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. Deploy to Vercel:
   - Install Vercel CLI: `npm i -g vercel`
   - Run `vercel` in the project directory
   - Follow the prompts to deploy

## Local Development

1. Run the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```
2. Run the clustering script:
   ```bash
   python clustering.py
   ```

## Features

- User questionnaire for matching
- Real-time chat using WebSocket
- Automated group clustering based on interests
- Google Sheets integration for data storage
- Vercel deployment for scalability

## Free Tier Limitations

- Google Sheets API: 500 requests per 100 seconds per project
- Vercel: 100GB bandwidth per month
- WebSocket connections: Limited by Vercel's serverless function timeout (10 seconds)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 