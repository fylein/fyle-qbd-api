import base64
import logging
from datetime import datetime
from typing import List

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, From
)

from quickbooks_desktop_api import settings


def send_email(receipient_emails: List[str], file_path:str):
    """
    Email IIF file to the user using sendgrid

    :param receipient_emails: (List[str])
    :param file_path: (str)
    """
    # Format template.html file with the data
    template_file = open('apps/utils/email/template.html', 'r')
    template = template_file.read().format(
        file_date=datetime.now().strftime("%Y-%m-%d")
    )
    template_file.close()

    message = Mail(
        from_email=From(settings.SENDGRID_FROM_EMAIL, 'Team Fyle'),
        to_emails=[email['email'] for email in receipient_emails],
        subject=f'Fyle: Your scheduled IIF file for {datetime.now().strftime("%Y-%m-%d")} is here!',
        html_content=template
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
            sendgrid = SendGridAPIClient(sendgrid_api_key)
            sendgrid.send(message)
