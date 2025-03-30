import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Tuple

# OAuth Scopes (Gmail sending only)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Authenticates using your credentials.json"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def create_message(to_email: str, subject: str, html_content: str, pdf_bytes: bytes = None, poster_bytes: bytes = None) -> dict:
    """Creates the email message with optional attachments"""
    msg = MIMEMultipart()
    msg['to'] = to_email
    msg['subject'] = subject
    
    msg.attach(MIMEText(html_content, 'html'))
    
    if pdf_bytes:
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename="Personalized_Itinerary.pdf"
        )
        msg.attach(pdf_attachment)
    
    if poster_bytes:
        poster_attachment = MIMEApplication(poster_bytes, _subtype="png")
        poster_attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename="Special_Offer_Poster.png"
        )
        msg.attach(poster_attachment)
    
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

def send_email(to_email: str, subject: str, html_content: str, pdf_bytes: bytes = None, poster_bytes: bytes = None) -> Tuple[bool, str]:
    """Sends email using your Gmail API credentials"""
    try:
        service = get_gmail_service()
        message = create_message(to_email, subject, html_content, pdf_bytes, poster_bytes)
        service.users().messages().send(
            userId="me",
            body=message
        ).execute()
        return True, f"Email sent to {to_email}"
    
    except HttpError as error:
        return False, f"Gmail API error: {str(error)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"