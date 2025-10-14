from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
import sendgrid, os
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

router = APIRouter(prefix="/api/email", tags=["user"])
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

class SendEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body: str

@router.post("/send")
def send_group_email(request: SendEmailRequest):
    print(SENDGRID_API_KEY)
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)  # Project API key here
    message = Mail(
        from_email='mvretna@gmail.com',
        to_emails=request.to_email,
        subject=request.subject,
        plain_text_content=request.body
    )
    try:
        sg.send(message)
        print("Email sent!")
        return True
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False
