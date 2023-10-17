# System imports
import os
import uuid
from datetime import datetime, timedelta

import urllib3
from exchangelib import Account, Configuration, Credentials, DELEGATE, EWSDateTime
from exchangelib import Message, Mailbox, FileAttachment, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

import BPMN_RPA.WorkflowEngine


class Email:
    # Author: Joost van Gils
    # Version: 1.1.0
    # Date:  21-11-2019
    #
    # The BPMN-RPA Code module is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # The BPMN-RPA Code module is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <https://www.gnu.org/licenses/>.
    #
    # The BPMN-RPA Code module is based on the ExchangeLib library. The Exchangelib library is licensed under the BSD 2-Clause "Simplified" License:
    # Copyright (c) 2009 Erik Cederstrand <erik@cederstrand.dk>
    #
    # Redistribution and use in source and binary forms, with or without modification, are
    # permitted provided that the following conditions are met:
    #
    #    1. Redistributions of source code must retain the above copyright notice, this list of
    #       conditions and the following disclaimer.
    #
    #    2. Redistributions in binary form must reproduce the above copyright notice, this list
    #    of conditions and the following disclaimer in the documentation and/or other materials
    #    provided with the distribution.
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
    # OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
    # MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    # COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
    # GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
    # AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    # NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
    # OF THE POSSIBILITY OF SUCH DAMAGE.

    def __init__(self, emailaddress: str, username: str, password: str):
        """
        Class for both creating, sending and reading emails from office365 Exchange.
        Use your emailaddress and your password to access your email account.
        You MUST use an app-password when 2-factor authentication is enabled.
        Please see: https://docs.microsoft.com/en-us/azure/active-directory/user-help/multi-factor-authentication-end-user-app-passwords for how to create an app password.
        :param username: The username (not the emailaddress) of the mailbox to connect to.
        :param emailaddress: The emailaddress of the mailbox to connect to.
        :param password: The password of the mailbox to connect to.
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        os.environ['NO_PROXY'] = 'xxx'
        BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
        self.username = username
        self.password = password
        self.emailaddress = emailaddress
        creds = Credentials(username=self.username, password=self.password)
        config = Configuration(credentials=creds, service_endpoint="https://outlook.office365.com/ews/exchange.asmx")
        self.account = Account(primary_smtp_address=self.emailaddress, credentials=creds, autodiscover=False,
                               config=config, access_type=DELEGATE)
        self.sql = None

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

    def send_email(self, subject: str, body: str, recipients: any, cc_recipients: any = None, html: bool = True, send_reply_to: any = None, attachments: any = None):
        """
        Send an email-message.
        :param subject: the subject of the email.
        :param body: the body text of the email.
        :param recipients: A string array of emailaddresses of the persons who need to receive the email.
        :param cc_recipients: Optional. A string array of emailaddresses of the persons who need to receive a carbon copy of the email.
        :param html: Optional. Boolean which indicates wether the email needs to be in HTML format.
        :param send_reply_to: Optional.  A string array of emailaddresses of the persons who need to receive the reply that will be sent origination from this email.
        :param attachments:  Optional. A string array of file locations of the files that need to be added as an attachment to this email.
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
            if not recipients.__contains__(",") and not recipients.__contains__(";"):
                tmp = [recipients]
            recipients = tmp
        if len(recipients) > 0:
            for recipient in recipients:
                if len(recipient) > 0:
                    to_recipients.append(Mailbox(email_address=recipient))
        else:
            to_recipients = None
        # CC-recipients
        if ccrecipients is not None:
            # it is a string, so make a list of it
            tmp = []
            if ccrecipients.__contains__(","):
                for recip in ccrecipients.split(","):
                    tmp.append(recip.strip())
            if ccrecipients.__contains__(";"):
                for recip in ccrecipients.split(";"):
                    tmp.append(recip.strip())
            if not ccrecipients.__contains__(",") and not ccrecipients.__contains__(";"):
                tmp = [ccrecipients]
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
            # it is a string, so make a list of it
            tmp = []
            if send_reply_to.__contains__(","):
                for recip in send_reply_to.split(","):
                    tmp.append(recip.strip())
            if send_reply_to.__contains__(";"):
                for recip in send_reply_to.split(";"):
                    tmp.append(recip.strip())
            if not send_reply_to.__contains__(",") and not send_reply_to.__contains__(";"):
                tmp = [send_reply_to]
            send_reply_to = tmp
            if len(send_reply_to) > 0:
                for rec in send_reply_to:
                    if len(rec) > 0:
                        replyto_recipients.append(Mailbox(email_address=rec))
            else:
                replyto_recipients = None
        else:
            replyto_recipients = None
        # sennd Email (only when there are recipients)
        if to_recipients is not None:
            # Create message
            if html:
                body = HTMLBody(body)
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

    def get_unread_emails(self, last_days: any = -1):
        """
        Retreiving unread email messages from the Inbox.
        :param last_days: Optional. Integer which indicates from how many days in the past the unread emails need to be retreived.
        :return: An array of email objects containing the unread emails from the Inbox.
        """
        if int(last_days) > -1:
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
        Retreive all email messages from the Inbox folder.
        :return: Yield item: an email item from the Inbox.
        """
        for item in self.account.inbox.all():
            yield item

    def get_all_emails_lite(self):
        """
        Retreive all email messages from the Inbox folder, but with a field restriction (for better performance).
        :return: Yield item: an email item from the Inbox.
        """
        for item in self.account.inbox.all().only('id', 'datetime_received', 'subject', 'body', 'to_recipients',
                                                  'cc_recipients', 'senther', 'conversation_id', 'attachments'):
            if item.id is not None:
                yield item

    def delete_email(self, msg):
        """
        Delete an email message.
        :param msg: The email message to delete.
        """
        msg.delete()

    def save_attachments(self, msg, folderpath):
        """
        Save all attachments of the email message to the specified folder
        :param msg: The email message object.
        :param folderpath: The path to the folder where the attachments will be saved.
        :return: A list with the attachment filenames
        """
        retn = []
        for attachment in msg.attachments:
            retn.append(attachment.name)
            fpath = os.path.join(folderpath, attachment.name)
            with open(fpath, 'wb') as f:
                f.write(attachment.content)
        return retn

    def get_contacts(self):
        """
        Get all contacts of this account
        :return: A list with contact objects
        """
        folder = self.account.contacts
        retn = []
        for p in folder.all():
            retn.append(p)
        return retn

    def get_contact_by_email(self, emailaddress):
        """
        Get a contacts of this account by it's emailaddress
        :return: The contact object
        """
        folder = self.account.contacts
        retn = []
        for p in folder.all().filter(email_addresses__icontains=emailaddress ):
            retn.append(p)
        return retn

    def get_contacts_with_birthday_today(self):
        """
        Get all contacts of this account whom have their birthday today
        :return: A list with contact objects whom have their birthday today
        """
        folder = self.account.contacts
        retn = []
        for p in folder.all().filter(birthday=datetime.today()):
            retn.append(p)
        return retn

    def send_question_with_options(self, recipient, subject, possible_answers, headertext="", footertext="", warningtext="This answer will be processed automatically. Please do not edit your answer. Any additional text will not be read.", sendReplyTo = ""):
        """
        Ask questions by email and store the question parameters in the Orhcestrator database, so answers can be collected when answers are received.
        :param recipient: The emailaddress of the recipient. This should be a single email address.
        :param subject: The subject of the email to send
        :param headertext: Optional. The text that is displayed above the questions
        :param footertext: Optional. The text that is displayed below the questions
        :param possible_answers: A comma separated string with possible answers that the recipient can reply with. Each answer will be shown as a link in the email body.
        :param warningtext: Optional. The text that is added to the answer to notify the recipient that answers cannot be edited.
        :param sendReplyTo: Optional. The emailaddress where answers will be received.
        """
        if len(sendReplyTo)==0:
            sendReplyTo = self.emailaddress
        body=f"""{headertext}<br><br><ul>"""
        question_id = uuid.uuid4().hex
        if self.sql is None:
            self.sql = BPMN_RPA.WorkflowEngine.SQL(BPMN_RPA.WorkflowEngine.WorkflowEngine.get_db_path())
        for answ in possible_answers.split(","):
            answer_id = uuid.uuid4().hex
            questiontext = str(headertext + ' ' + footertext).strip()
            self.sql.run_sql(f"INSERT INTO Survey (recipient, question_id, question, answer_id, answer) VALUES ('{recipient}','{question_id}', '{questiontext}', '{answer_id}', '{str(answ).strip()}');")
            body += f"<li style=\"mso-special-format:bullet;\"><a href='mailto:{sendReplyTo}?subject=Reply to question {question_id}&body={str(answ).strip()}%0D%0AConfirmation code: {answer_id}%0D%0A%0D%0A{warningtext}'>{str(answ).strip()}</a></li>"
        body += f"</ul><br><br>{footertext}"
        self.send_email(subject, body, [recipient])

    def is_email_answer_to_question(self, emailmessage):
        """
        Indicator whether the email message is an answer to a question that was send earlier. The answer will be recognized by the sendername, the question ID and the confirmation code.
        :param emailmessage: The email message to investigate.
        :return: True or False.
        """
        if str(emailmessage.subject).startswith("Reply to question "):
            question_id = str(emailmessage.subject).replace("Reply to question ", "")
        else:
            return False
        if self.sql is None:
            self.sql = BPMN_RPA.WorkflowEngine.SQL(BPMN_RPA.WorkflowEngine.WorkflowEngine.get_db_path())
        sql = f"SELECT * FROM Survey WHERE question_id='{question_id}' AND Recipient = '{emailmessage.sender.email_address}';"
        curs = self.sql.connection.cursor()
        curs.execute(sql)
        row = curs.fetchone()
        if row is None:
            return False
        return True

    def get_email_answer_to_question(self, emailmessage, delete_from_database=True):
        """
        Get the answer from the email message. The answer will be recognized by the sendername, the question ID and the confirmation code.
        :param emailmessage: The email message to get the answer of.
        :param delete_from_database: Optional. Indicator whether to delete the question send from the Orhcestrator database.
        :return: True or False.
        """
        if str(emailmessage.subject).startswith("Reply to question "):
            question_id = str(emailmessage.subject).replace("Reply to question ", "")
        else:
            return False
        if self.sql is None:
            self.sql = BPMN_RPA.WorkflowEngine.SQL(BPMN_RPA.WorkflowEngine.WorkflowEngine.get_db_path())
        answer_id = str(str(emailmessage.body).split("Confirmation code: ")[1]).split(" ")[0]
        sql = f"SELECT answer FROM Survey WHERE question_id='{question_id}' AND Recipient = '{emailmessage.sender.email_address}' AND answer_id='{answer_id}';"
        curs = self.sql.connection.cursor()
        curs.execute(sql)
        row = curs.fetchone()
        retn = None
        if row is not None:
            retn = row[0]
            if delete_from_database:
                self.sql.run_sql(f"DELETE FROM Survey WHERE question_id='{question_id}' AND Recipient = '{emailmessage.sender.email_address}';")
            else:
                self.sql.run_sql(f"UPDATE Survey SET received=1 WHERE question_id='{question_id}' AND Recipient = '{emailmessage.sender.email_address}' AND answer_id='{answer_id}';")
        return retn



