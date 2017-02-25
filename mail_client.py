
import smtplib
from email.mime.text import MIMEText

class EmailClient(object):

    def __init__(self, sender, password, server='smtp.gmail.com'):
        self.sender = sender
        self.server = smtplib.SMTP_SSL(server, 465)
        self.server.login(self.sender, password)

    def send(self, subject, message, recipients):
        message = MIMEText(message)
        message['subject'] = subject
        self.server.sendmail(self.sender, recipients, message.as_string())

