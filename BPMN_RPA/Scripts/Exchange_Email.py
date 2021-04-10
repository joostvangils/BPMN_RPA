# System imports
import os

import requests
import urllib3
from datetime import datetime, timedelta
from typing import List
from exchangelib import Account, Configuration, Credentials, DELEGATE, EWSDateTime
from exchangelib import Message, Mailbox, FileAttachment, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['NO_PROXY'] = 'xxx'

class Email:
    # Author: Joost van Gils
    # Version: 1.1.0
    # Date:  21-11-2019

    def __init__(self, emailaddress: str, username: str, password: str):
        """
        Class for both creating, sending and reading emails.
        Use your emailaddress and your password to access your email account.
        You MUST use an app-password when 2-factor authentication is enabled.
        Please see: https://docs.microsoft.com/en-us/azure/active-directory/user-help/multi-factor-authentication-end-user-app-passwords for how to create an app password.
        :param username: The username (not the emailaddress) of the mailbox to connect to.
        :param emailaddress: The emailaddress of the mailbox to connect to.
        :param password: The password of the mailbox to connect to.
        """
        BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
        self.username = username
        self.password = password
        self.emailaddress = emailaddress
        creds = Credentials(username=self.username, password=self.password)
        config = Configuration(credentials=creds, service_endpoint="https://outlook.office365.com/ews/exchange.asmx")
        self.account = Account(primary_smtp_address=self.emailaddress, credentials=creds, autodiscover=False,
                               config=config, access_type=DELEGATE)

    def move_message_to_inbox_subfolder(self, msg: object, folder: str):
        """
        Move an email to a subfolder of the Inbox.
        :param msg: The email object that must be moved.
        :param folder: the name of the subfolder of the Inbox.
        """
        to_folder = self.account.inbox / folder
        getattr(msg, "move")(to_folder)

    def count_messages(self) -> int:
        """
        Count the total of unread messages in the Inbox folder.
        :return: The total of unread messages in the Inbox folder.
        """
        # self.account.inbox.filter(is_read=False)
        total = self.account.inbox.all()
        self.account.inbox.filter(is_read=False)
        return total

    def send_email(self, subject: str, body: str, recipients: List[str], cc_recipients: List[str] = None, html: bool = True, send_reply_to: List[str] = None, attachments: List[str] = None):
        """
        Send an email-message.
        :param subject: the subject of the email.
        :param body: the body text of the email.
        :param recipients: A string array of emailaddresses of the persons who need to receive the email.
        :param cc_recipients: A string array of emailaddresses of the persons who need to receive a carbon copy of the email.
        :param html: Optional. Boolean which indicates wether the email needs to be in HTML format.
        :param send_reply_to:  A string array of emailaddresses of the persons who need to receive the reply that will be sent origination from this email.
        :param attachments:  A string array of file locations of the files that need to be added as an attachment to this email.
        """
        to_recipients = []
        replyto_recipients = []
        ccrecipients = cc_recipients
        cc_recipients = []
        # Recipients
        if isinstance(recipients, str) and len(recipients) > 0:
            # it is a string, so make a list of it
            tmp = []
            if recipients.__contains__(","):
                for recip in recipients.split(","):
                    tmp.append(recip.strip())
            if recipients.__contains__(";"):
                for recip in recipients.split(";"):
                    tmp.append(recip.strip())
            recipients = tmp
        if len(recipients) > 0:
            for recipient in recipients:
                if len(recipient) > 0:
                    to_recipients.append(Mailbox(email_address=recipient))
        else:
            to_recipients = None
        # CC-recipients
        if ccrecipients is not None:
            if isinstance(ccrecipients, str) and len(ccrecipients) > 0:
                # it is a string, so make a list of it
                tmp = []
                for recip in ccrecipients.split(","):
                    tmp.append(recip.strip())
                ccrecipients = tmp
            if len(ccrecipients) > 0:
                for rec in ccrecipients:
                    if len(rec) > 0:
                        cc_recipients.append(Mailbox(email_address=rec))
            else:
                cc_recipients = None
        else:
            cc_recipients = None
        # Reply-to recipients
        if send_reply_to is not None:
            if isinstance(send_reply_to, str) and len(send_reply_to) > 0:
                # it is a string, so make a list of it
                tmp = []
                for recip in send_reply_to.split(","):
                    tmp.append(recip.strip())
                send_reply_to = tmp
            if len(send_reply_to) > 0:
                for rec in send_reply_to:
                    if len(rec) > 0:
                        replyto_recipients.append(Mailbox(email_address=rec))
            else:
                replyto_recipients = None
        else:
            replyto_recipients = None
        # Email versturen (alleen als er ontvangers zijn)
        if to_recipients is not None:
            # Create message
            if html:
                body = HTMLBody(body)
            else:
                body = body
            m = Message(account=self.account,
                        folder=self.account.sent,
                        subject=subject,
                        body=body,
                        to_recipients=to_recipients, reply_to=replyto_recipients, cc_recipients=cc_recipients)
            Message()
            # attach files
            if attachments is not None:
                for att in attachments:
                    ats = att.replace("\\", "/").replace("\\\\", "/")
                    if os.path.exists(ats):
                        bestand = os.path.basename(ats)
                        with open(ats, 'rb') as f:
                            content = f.read()
                        file = FileAttachment(name=bestand, content=content)
                        m.attach(file)

            m.send_and_save()
            return m
        else:
            print("Recipients needs to be an array!")

    def get_unread_emails(self, last_days: int = -1):
        """
        Retreiving unread email messages from the Inbox.
        :param last_days: Optional. Integer which indicates from how many days in the past the unread emails need to be retreived.
        :return: An array of email objects containing the unread emails from the Inbox.
        """
        if last_days > -1:
            today = datetime.today()
            startday = today - timedelta(days=last_days)
            start = self.account.default_timezone.localize(
                EWSDateTime(startday.year, startday.month, startday.day, 0, 0, 1))
            finish = self.account.default_timezone.localize(
                EWSDateTime(today.year, today.month, today.day, 23, 59, 59))
            return self.account.inbox.filter(is_read=False, datetime_received__range=(start, finish))
        else:
            return self.account.inbox.filter(is_read=False)

    def get_all_emails(self):
        """
        Retreive all unread email messages from the Inbox folder.
        :return: Yield item: an email item from the Inbox.
        """
        for item in self.account.inbox.all():
            yield item

    def get_all_emails_lite(self):
        """
        Retreive all unread email messages from the Inbox folder, but with a field restriction (for better performance).
        :return: Yield item: an email item from the Inbox.
        """
        for item in self.account.inbox.all().only('id', 'datetime_received', 'subject', 'body', 'to_recipients',
                                                  'cc_recipients', 'senther', 'conversation_id', 'attachments'):
            if item.id is not None:
                yield item
