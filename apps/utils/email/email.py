import base64
from datetime import datetime
from typing import List

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment
)

from quickbooks_desktop_api import settings


def send_email(receipient_emails: List[str], file_path:str):
    """
    Email IIF file to the user using sendgrid

    :param receipient_emails: (List[str])
    :param file_path: (str)
    """
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=receipient_emails,
        subject='QuickBooks Desktop IIF File {}'.format(datetime.now().strftime('%Y-%m-%d')),
        html_content='Please find attached the IIF file for your QuickBooks Desktop'
    )

    sendgrid_api_key = settings.SENDGRID_API_KEY

    with open(file_path, 'rb') as file:
        encoded = base64.b64encode(file.read()).decode()
        attachment = Attachment(
            file_content=encoded,
            file_type='text/plain',
            file_name=file_path.split('/')[-1],
            disposition='attachment'
        )

        message.attachment = attachment
        if sendgrid_api_key:
            sendgrid = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sendgrid.send(message)
