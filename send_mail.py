#!/Anaconda3/python
from datetime import datetime
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .logger import mylogger

TO_EMAILS = []  # iterate over recipients
FROM_EMAIL = ''  # there is only one sender address


def send_email(mylogger: object, body: str):
  """
  :param mylogger: an application logger
  :param body: your email message body, containing HTML
  """
    if body is not None:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M")
        subject = f'-{date}-{time}'  # set custom email subject here
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAILS,
            subject=subject,
            html_content=body
        )
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        try:
            response = sg.send(message)
            mylogger.info(f'Email resp: {response.status_code} {date} {time}')
            success = True
        except Exception as e:
            log_line = f'Exception {e}'
            mylogger.error(log_line)
            success = False

        return success, response
    else:
        mylogger.info(f"There are no new alerts to send.")

        return False, None
