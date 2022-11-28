import base64
import json
import sys
from datetime import datetime, timedelta
import jwt
import msal
import requests
import ctypes
from ctypes import wintypes
from msal_extensions import FilePersistenceWithDataProtection, KeychainPersistence, FilePersistence, PersistedTokenCache


# The BPMN-RPA MsGraph module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA MsGraph module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class ms_graph:

    # create an app in https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview
    # after that, create secret and set app permissions in https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps
    # don't forget to grant admin consent in that same screen
    # on error JWT decode: install 'pip install PyJWT==1.7.1'

    def __init__(self, client_secret, user_name, client_id, tenant_id):
        """
        Initialize the class to make use of the Microsoft Graph API. To make this class work:
        1. Create an app in https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview
        2. After that, create secret and set app permissions in https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps
        3. Don't forget to grant admin consent in that same screen
        :param client_secret: The client secret value of the app registration created under Certificates & secrets.
        :param user_name: The user name of the user that will be used to authenticate.
        :param client_id: The Application (client) ID of the app registration.
        :param tenant_id: The tenant id of the app registration created under Overview (see https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Overview).
        """
        self.client_secret_value = client_secret  # The client secret value of the app registration created under Certificates & secrets
        self.username = user_name
        self.headers = None
        self.graphURI = 'https://graph.microsoft.com'
        self.tenantID = tenant_id  # https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Overview
        self.authority = 'https://login.microsoftonline.com/' + self.tenantID
        self.clientID = client_id  # The Application (client) ID of the app registration
        self.scope = ["User.ReadWrite.All", "Mail.ReadWrite.Shared", "Contacts.ReadWrite", "Contacts.ReadWrite.Shared", "AccessReview.ReadWrite.All", "AdministrativeUnit.ReadWrite.All"]
        self.tokenExpiry = None

    def msal_persistence(self, location, fallback_to_plaintext=False):
        """
        Build a suitable persistence instance based your current OS
        :param location: The location of the token cache file.
        :param fallback_to_plaintext: If True, the cache will be encrypted if possible, but will fall back to plaintext if encryption is not available.
        :return: A suitable persistence instance.
        """
        try:
            if sys.platform.startswith('win'):
                return FilePersistenceWithDataProtection(location)
            if sys.platform.startswith('darwin'):
                return KeychainPersistence(location, "my_service_name", "my_account_name")
            return FilePersistence(location)
        except Exception as e:
            print("Failed to create a persistence. Falling back to plaintext")
            print(e)
            return FilePersistence(location, fallback_to_plaintext)


    def msal_cache_accounts(self, clientID, authority):
        """
        Get the accounts from the cache.
        :param clientID: The Application (client) ID of the app registration.
        :param authority: The authority of the app registration.
        :return: The accounts from the cache.
        """
        # Accounts
        try:
            persistence = self.msal_persistence("token_cache.bin")
            print("MSAL persistence cache encrypted: ", persistence.is_encrypted)
            cache = PersistedTokenCache(persistence)
            app = msal.PublicClientApplication(
                client_id=clientID, authority=authority, token_cache=cache)
            accounts = app.get_accounts()
            print(accounts)
            return accounts
        except Exception as e:
            print("Failed to get accounts from cache")
            print(e)
            return None

    def msal_delegated_refresh(self, clientID, scope, authority, account):
        """
        Refresh the token using the cache.
        :param clientID: The Application (client) ID of the app registration.
        :param scope: The scope of the app registration.
        :param authority: The authority of the app registration.
        :param account: The account to use.
        :return: The refreshed token.
        """
        try:
            persistence = self.msal_persistence("token_cache.bin")
            cache = PersistedTokenCache(persistence)
            app = msal.PublicClientApplication(
                client_id=clientID, authority=authority, token_cache=cache)
            result = app.acquire_token_silent_with_error(
                scopes=scope, account=account)
            return result
        except Exception as e:
            print("Failed to refresh token")
            print(e)
            return None

    def msal_delegated_refresh_force(self, clientID, scope, authority, account):
        """
        Refresh the token using the cache.
        :param clientID: The Application (client) ID of the app registration.
        :param scope: The scope of the app registration.
        :param authority: The authority of the app registration.
        :param account: The account to use.
        :return: The refreshed token.
        """
        try:
            persistence = self.msal_persistence("token_cache.bin")
            cache = PersistedTokenCache(persistence)
            app = msal.PublicClientApplication(
                client_id=clientID, authority=authority, token_cache=cache)
            result = app.acquire_token_silent_with_error(
                scopes=scope, account=account, force_refresh=True)
            return result
        except Exception as e:
            print("Failed to refresh token")
            print(e)
            return None

    def msal_delegated_device_flow(self, clientID, scope, authority):
        """
        Get a token using the device flow.
        :param clientID: The Application (client) ID of the app registration.
        :param scope: The scope of the app registration.
        :param authority: The authority of the app registration.
        :return: The token.
        """
        try:
            print("Initiate Device Code Flow to get an AAD Access Token.")
            print("Open a browser window and paste in the URL below and then enter the Code. CTRL+C to cancel.")
            persistence = self.msal_persistence("token_cache.bin")
            cache = PersistedTokenCache(persistence)
            app = msal.PublicClientApplication(client_id=clientID, authority=authority, token_cache=cache)
            flow = app.initiate_device_flow(scopes=scope)
            if "user_code" not in flow:
                raise ValueError("Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))
            print(flow["message"])
            sys.stdout.flush()
            result = app.acquire_token_by_device_flow(flow)
            return result
        except Exception as e:
            print("Failed to get token using device flow")
            print(e)
            return None

    def msal_jwt_expiry(self, accessToken):
        """
        Get the expiry of the token.
        :param accessToken: The access token.
        :return: The expiry of the token.
        """
        decodedAccessToken = jwt.decode(accessToken, verify=False)
        return decodedAccessToken['exp']
        accessTokenFormatted = json.dumps(decodedAccessToken, indent=2)
        # Token Expiry
        tokenExpiry = datetime.fromtimestamp(int(decodedAccessToken['exp']))
        print("Token Expires at: " + str(tokenExpiry))
        return tokenExpiry

    def msgraph_request(self, resource, requestHeaders):
        """
        Make a request to the Microsoft Graph API.
        :param resource: The resource to request.
        :param requestHeaders: The headers to use.
        :return: The response.
        """
        # Request
        results = requests.get(resource, headers=requestHeaders).json()
        return results

    class Children(object):
        pass

    class MessageObject:
        def __init__(self, d=None):
            if d is not None:
                for key, value in d.items():
                    setattr(self, key, value)

    def get_access_token(self, force_renew=False):
        """
        Retrieve an access token.
        :param force_renew: Optional. Force a new delegated_device_flow for authentication when updated the app permissions.
        :return: The access token.
        """
        # First register app in Azure AD via url https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/~/AppAppsPreview
        # After that, create secret and set app permissions in https://aad.portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps
        # Don't forget to grant admin consent in that same screen
        # data = {'response_type': 'code', 'client_id': self.client_id, 'redirect_uri': 'https://localhost', 'client_secret': self.client_secret_value, 'response_mode': 'query', 'grant_type': 'client_credentials', 'state': '12345', 'scope': 'https://graph.microsoft.com/.default'}
        # response = requests.post('https://login.microsoftonline.com/valuestream.nl/oauth2/v2.0/token', data=data)
        accounts = self.msal_cache_accounts(self.clientID, self.authority)
        result = None
        if accounts:
            for account in accounts:
                if account['username'] == self.username:
                    myAccount = account
                    print("Found account in MSAL Cache: " + account['username'])
                    print("Obtaining a new Access Token using the Refresh Token")
                    result = self.msal_delegated_refresh(self.clientID, self.scope, self.authority, myAccount)

                    if result is None or force_renew:
                        # Get a new Access Token using the Device Code Flow
                        result = self.msal_delegated_device_flow(self.clientID, self.scope, self.authority)
                    else:
                        if "error" in str(result):
                            # Get a new Access Token using the Device Code Flow
                            result = self.msal_delegated_device_flow(self.clientID, self.scope, self.authority)
                        if result["access_token"]:
                            self.msal_jwt_expiry(result["access_token"])
        else:
            # Get a new Access Token using the Device Code Flow
            result = self.msal_delegated_device_flow(self.clientID, self.scope, self.authority)
            if result["access_token"]:
                self.msal_jwt_expiry(result["access_token"])
        self.headers = {'Authorization': 'Bearer ' + result["access_token"], 'Content-Type': 'application/json'}

    def get_users(self):
        """
        Get all users.
        :return: A list of users.
        """
        if self.headers is None:
            self.get_access_token()
        response = requests.get('https://graph.microsoft.com/v1.0/users', headers=self.headers)
        return response.json()["value"]

    def get_user(self, email):
        """
        Get user information.
        :param email: The email address of the user.
        :return: The user information.
        """
        if self.headers is None:
            self.get_access_token()
        response = requests.get('https://graph.microsoft.com/v1.0/users/{}'.format(email), headers=self.headers)
        return response.json()

    def get_user_id(self, email):
        """
        Get the user id of a mailbox.
        :param email: The email address of the mailbox.
        :return: The user id of the mailbox.
        """
        if email is None:
            return None
        if self.headers is None:
            self.get_access_token()
        response = requests.get('https://graph.microsoft.com/v1.0/users/{}'.format(email), headers=self.headers)
        return response.json()["id"]

    def get_messages(self, email, number=10, with_attachments=True):
        """
        Get messages from mailbox.
        :param email: The email address of the mailbox.
        :param number: The number of messages to retrieve.
        :param with_attachments: Optional. If True, attachments will be retrieved.
        :return: A list of messages.
        """
        retn = []
        if self.headers is None:
            self.get_access_token()
        id = self.get_user_id(email)
        response = requests.get(f'https://graph.microsoft.com/v1.0/users/{id}/mailFolders/Inbox/messages?$top={number}', headers=self.headers)
        for message in response.json()["value"]:
            if with_attachments:
                response = requests.get(f'https://graph.microsoft.com/v1.0/users/{id}/messages/{message["id"]}/attachments', headers=self.headers)
                if response.json()["value"] != []:
                    message["attachments"] = response.json()["value"]
            retn.append(self.MessageObject(message))
        return retn

    def send_email(self, email_from, email_to, subject, body):
        """
        Send an email.
        :param email_from: The email address of the sender.
        :param email_to: The email address of the recipient.
        :param subject: The subject of the email message.
        :param body: The body of the email message.
        """
        if self.headers is None:
            self.get_access_token()
        id = self.get_user_id(email_from)
        data = {"message": {"subject": subject, "body": {"contentType": "Html", "content": body}, "toRecipients": [{"emailAddress": {"address": email_to}}]}}
        response = requests.post(f'https://graph.microsoft.com/v1.0/users/{id}/sendMail', headers=self.headers, json=data)

    def save_attachment(self, attachment, filename):
        """
        Save attachment to file
        :param attachment: The attachment to save
        :param filename: The filename to save the attachment as
        """
        with open(filename, "wb") as f:
            f.write(base64.b64decode(attachment['contentBytes']))

    def get_appointments(self, startdate: datetime = datetime.now(), enddate: datetime = datetime.now() + timedelta(hours=8), of_email: str = ""):
        """
        Get appointments from calendar.
        :param startdate: Optional. The start date of the appointments to retrieve. If not specified, the current date from 00:00:01 hrs will be used.
        :param enddate: Optional. The end date of the appointments to retrieve. If not specified, the startdate + 8 hours will be used.
        :param of_email: Optional. The email address of the mailbox to retrieve the appointments from. If not specified, the mailbox of the user will be used.
        :return: A list of appointments.
        """
        if self.headers is None:
            self.get_access_token()
        if of_email == "":
            id = self.get_user_id(self.username)
        else:
            id = self.get_user_id(of_email)
        response = requests.get(f"https://graph.microsoft.com/v1.0/users/{id}/calendar/events?$filter=start/dateTime ge '{startdate.strftime('%Y-%m-%dT%H:%M:%SZ')}' and start/dateTime lt '{enddate.strftime('%Y-%m-%dT%H:%M:%SZ')}'", headers=self.headers)
        return response.json()["value"]

    def create_appointment(self, subject: str, startdatetime: datetime, enddatetime: datetime, calendar_of_email: str = "", body: str = "", location: str = "", attendees: list = [], organizer: str = "", all_day: bool = False, recurrence_pattern: str = "", index: str = "", days_of_week: any = [], month: str = "", interval: int = 1, number_of_occurrences: int = 1):
        """
        Create appointment in calendar. Example: create_appointment("Test", datetime.now(), datetime.now() + timedelta(hours=1), "Test", "Test").
        :param subject: The subject of the appointment.
        :param startdatetime: The start date and time of the appointment.
        :param enddatetime: The end date and time of the appointment.
        :param location: Optional. The location of the appointment.
        :param attendees: Optional. A list of attendees.
        :param body: Optional. The body of the appointment.
        :param organizer: Optional. The emailaddress of the organizer of the appointment.
        :param calendar_of_email: Optional. The email address of the mailbox to create the appointment in. If not specified, the mailbox of the user will be used.
        :param all_day: Optional. If True, the appointment will be an all day appointment. Default is False.
        :param recurrence_pattern: Optional. The recurrence pattern of the appointment. Options: daily, weekly, monthly, yearly, 2 weekly, 3 weekly.
        :param index: Optional. The day index of the appointment. Options: first, second, third, fourth, last.
        :param days_of_week: Optional. The day (or days) of the week of the appointment. Options: sunday, monday, tuesday, wednesday, thursday, friday, saturday.
        :param month: Optional. The month of the appointment. Options: january, february, march, april, may, june, july, august, september, october, november, december.
        :param interval: Optional. The interval of the appointment. Default is 1.
        :param number_of_occurrences: Optional. The number of occurrences of the appointment. Default is 1.
        """
        if self.headers is None:
            self.get_access_token()
        if calendar_of_email == "":
            id = self.get_user_id(self.email)
        else:
            id = self.get_user_id(calendar_of_email)
        data = {"subject": subject, "start": {"dateTime": startdatetime.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": "UTC"}, "end": {"dateTime": enddatetime.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": "UTC"}, "body": {"contentType": "HTML", "content": body}, "location": {"displayName": location}, "attendees": []}
        for attendee in attendees:
            data["attendees"].append({"emailAddress": {"address": attendee}})
        if organizer != "":
            data["organizer"] = {"emailAddress": {"address": organizer}}
        if all_day:
            data["isAllDay"] = True
        if recurrence_pattern != "":
            if recurrence_pattern == "daily":
                data["recurrence"] = {"pattern": {"type": "daily", "interval": interval}, "range": {"type": "noEnd", "startDate": startdatetime.strftime("%Y-%m-%d %H:%M:%S")}}
            elif recurrence_pattern == "weekly":
                data["recurrence"] = {"pattern": {"type": "weekly", "interval": interval, "daysOfWeek": days_of_week}, "range": {"type": "noEnd", "startDate": startdatetime.strftime("%Y-%m-%d %H:%M:%S")}}
            elif recurrence_pattern == "monthly":
                data["recurrence"] = {"pattern": {"type": "absoluteMonthly", "interval": interval, "dayOfMonth": startdatetime.day}, "range": {"type": "noEnd", "startDate": startdatetime.strftime("%Y-%m-%d %H:%M:%S")}}
            elif recurrence_pattern == "yearly":
                data["recurrence"] = {"pattern": {"type": "absoluteYearly", "interval": interval, "month": month, "dayOfMonth": startdatetime.day}, "range": {"type": "noEnd", "startDate": startdatetime.strftime("%Y-%m-%d %H:%M:%S")}}
            elif recurrence_pattern == "2 weekly":
                data["recurrence"] = {"pattern": {"type": "weekly", "interval": 2, "daysOfWeek": days_of_week, "index": index}, "range": {"type": "noEnd", "startDate": startdatetime.strftime("%Y-%m-%d %H:%M:%S")}}
            elif recurrence_pattern == "3 weekly":
                data["recurrence"] = {"pattern": {"type": "weekly", "interval": 3, "daysOfWeek": days_of_week, "index": index}, "range": {"type": "noEnd", "startDate": startdatetime.strftime("%Y-%m-%d %H:%M:%S")}}
        response = requests.post(f'https://graph.microsoft.com/v1.0/users/{id}/events', headers=self.headers, json=data)
        return response.json()

    def get_contacts(self, of_email: str = ""):
        """
        Get contacts from the address book.
        :param of_email: Optional. The email address of the mailbox to get the contacts from. If not specified, the email address of the mailbox used to authenticate will be used.
        :return: A list of contacts.
        """
        if self.headers is None:
            self.get_access_token()
        if of_email == "":
            id = self.get_user_id(self.username)
        else:
            id = self.get_user_id(of_email)
        response = requests.get(f'https://graph.microsoft.com/v1.0/users/{id}/contacts', headers=self.headers)
        return response.json()["value"]
