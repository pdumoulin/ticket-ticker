
import pickle
import smtplib

from pprint import pformat
from email.mime.text import MIMEText

class EmailClient(object):

    def __init__(self, history_file, sender, password, server='smtp.gmail.com'):
        self.history_file = history_file
        self.history = pickle.load(open(history_file, 'rb'))

        self.sender = sender
        self.server = smtplib.SMTP_SSL(server, 465)
        self.server.login(self.sender, password)

    def _send(self, subject, message, recipients):
        message = MIMEText(message)
        message['subject'] = subject
        self.server.sendmail(self.sender, recipients, message.as_string())

    def _already_sent(self, listing, email):
        return email in self.history and listing.uid() in self.history[email]

    def _record_sent(self, listings, email):
        if email not in self.history:
            self.history[email] = []
        self.history[email] += [t.uid() for t in listings]
        pickle.dump(self.history, open(self.history_file, 'wb'))

    def send_event(self, emails, event, listings):
        num_sent = 0
        if len(emails) == 0:
            return num_sent
        new_listings = []
        for email in emails:
            new_listings += filter(lambda t: not self._already_sent(t, email), listings)
            if len(new_listings) > 0:
                self._record_sent(new_listings, email)
                output = event.output()
                for listing in new_listings:
                    output += listing.output()
                self._send(
                    'Ticket Alert! %s : %s' % (event.name, event.date),
                    output,
                    emails
                )
                num_sent += 1
        return num_sent
