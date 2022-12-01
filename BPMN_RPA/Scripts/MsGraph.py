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
#
# The BPMN-RPA MsGraph module is based on the JWT module (copyright Kohei YOSHIDA), which is licensed under the Apache License
#                            Version 2.0, January 2004
#                         http://www.apache.org/licenses/
#
#    TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
#
#    1. Definitions.
#
#       "License" shall mean the terms and conditions for use, reproduction,
#       and distribution as defined by Sections 1 through 9 of this document.
#
#       "Licensor" shall mean the copyright owner or entity authorized by
#       the copyright owner that is granting the License.
#
#       "Legal Entity" shall mean the union of the acting entity and all
#       other entities that control, are controlled by, or are under common
#       control with that entity. For the purposes of this definition,
#       "control" means (i) the power, direct or indirect, to cause the
#       direction or management of such entity, whether by contract or
#       otherwise, or (ii) ownership of fifty percent (50%) or more of the
#       outstanding shares, or (iii) beneficial ownership of such entity.
#
#       "You" (or "Your") shall mean an individual or Legal Entity
#       exercising permissions granted by this License.
#
#       "Source" form shall mean the preferred form for making modifications,
#       including but not limited to software source code, documentation
#       source, and configuration files.
#
#       "Object" form shall mean any form resulting from mechanical
#       transformation or translation of a Source form, including but
#       not limited to compiled object code, generated documentation,
#       and conversions to other media types.
#
#       "Work" shall mean the work of authorship, whether in Source or
#       Object form, made available under the License, as indicated by a
#       copyright notice that is included in or attached to the work
#       (an example is provided in the Appendix below).
#
#       "Derivative Works" shall mean any work, whether in Source or Object
#       form, that is based on (or derived from) the Work and for which the
#       editorial revisions, annotations, elaborations, or other modifications
#       represent, as a whole, an original work of authorship. For the purposes
#       of this License, Derivative Works shall not include works that remain
#       separable from, or merely link (or bind by name) to the interfaces of,
#       the Work and Derivative Works thereof.
#
#       "Contribution" shall mean any work of authorship, including
#       the original version of the Work and any modifications or additions
#       to that Work or Derivative Works thereof, that is intentionally
#       submitted to Licensor for inclusion in the Work by the copyright owner
#       or by an individual or Legal Entity authorized to submit on behalf of
#       the copyright owner. For the purposes of this definition, "submitted"
#       means any form of electronic, verbal, or written communication sent
#       to the Licensor or its representatives, including but not limited to
#       communication on electronic mailing lists, source code control systems,
#       and issue tracking systems that are managed by, or on behalf of, the
#       Licensor for the purpose of discussing and improving the Work, but
#       excluding communication that is conspicuously marked or otherwise
#       designated in writing by the copyright owner as "Not a Contribution."
#
#       "Contributor" shall mean Licensor and any individual or Legal Entity
#       on behalf of whom a Contribution has been received by Licensor and
#       subsequently incorporated within the Work.
#
#    2. Grant of Copyright License. Subject to the terms and conditions of
#       this License, each Contributor hereby grants to You a perpetual,
#       worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#       copyright license to reproduce, prepare Derivative Works of,
#       publicly display, publicly perform, sublicense, and distribute the
#       Work and such Derivative Works in Source or Object form.
#
#    3. Grant of Patent License. Subject to the terms and conditions of
#       this License, each Contributor hereby grants to You a perpetual,
#       worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#       (except as stated in this section) patent license to make, have made,
#       use, offer to sell, sell, import, and otherwise transfer the Work,
#       where such license applies only to those patent claims licensable
#       by such Contributor that are necessarily infringed by their
#       Contribution(s) alone or by combination of their Contribution(s)
#       with the Work to which such Contribution(s) was submitted. If You
#       institute patent litigation against any entity (including a
#       cross-claim or counterclaim in a lawsuit) alleging that the Work
#       or a Contribution incorporated within the Work constitutes direct
#       or contributory patent infringement, then any patent licenses
#       granted to You under this License for that Work shall terminate
#       as of the date such litigation is filed.
#
#    4. Redistribution. You may reproduce and distribute copies of the
#       Work or Derivative Works thereof in any medium, with or without
#       modifications, and in Source or Object form, provided that You
#       meet the following conditions:
#
#       (a) You must give any other recipients of the Work or
#           Derivative Works a copy of this License; and
#
#       (b) You must cause any modified files to carry prominent notices
#           stating that You changed the files; and
#
#       (c) You must retain, in the Source form of any Derivative Works
#           that You distribute, all copyright, patent, trademark, and
#           attribution notices from the Source form of the Work,
#           excluding those notices that do not pertain to any part of
#           the Derivative Works; and
#
#       (d) If the Work includes a "NOTICE" text file as part of its
#           distribution, then any Derivative Works that You distribute must
#           include a readable copy of the attribution notices contained
#           within such NOTICE file, excluding those notices that do not
#           pertain to any part of the Derivative Works, in at least one
#           of the following places: within a NOTICE text file distributed
#           as part of the Derivative Works; within the Source form or
#           documentation, if provided along with the Derivative Works; or,
#           within a display generated by the Derivative Works, if and
#           wherever such third-party notices normally appear. The contents
#           of the NOTICE file are for informational purposes only and
#           do not modify the License. You may add Your own attribution
#           notices within Derivative Works that You distribute, alongside
#           or as an addendum to the NOTICE text from the Work, provided
#           that such additional attribution notices cannot be construed
#           as modifying the License.
#
#       You may add Your own copyright statement to Your modifications and
#       may provide additional or different license terms and conditions
#       for use, reproduction, or distribution of Your modifications, or
#       for any such Derivative Works as a whole, provided Your use,
#       reproduction, and distribution of the Work otherwise complies with
#       the conditions stated in this License.
#
#    5. Submission of Contributions. Unless You explicitly state otherwise,
#       any Contribution intentionally submitted for inclusion in the Work
#       by You to the Licensor shall be under the terms and conditions of
#       this License, without any additional terms or conditions.
#       Notwithstanding the above, nothing herein shall supersede or modify
#       the terms of any separate license agreement you may have executed
#       with Licensor regarding such Contributions.
#
#    6. Trademarks. This License does not grant permission to use the trade
#       names, trademarks, service marks, or product names of the Licensor,
#       except as required for reasonable and customary use in describing the
#       origin of the Work and reproducing the content of the NOTICE file.
#
#    7. Disclaimer of Warranty. Unless required by applicable law or
#       agreed to in writing, Licensor provides the Work (and each
#       Contributor provides its Contributions) on an "AS IS" BASIS,
#       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#       implied, including, without limitation, any warranties or conditions
#       of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
#       PARTICULAR PURPOSE. You are solely responsible for determining the
#       appropriateness of using or redistributing the Work and assume any
#       risks associated with Your exercise of permissions under this License.
#
#    8. Limitation of Liability. In no event and under no legal theory,
#       whether in tort (including negligence), contract, or otherwise,
#       unless required by applicable law (such as deliberate and grossly
#       negligent acts) or agreed to in writing, shall any Contributor be
#       liable to You for damages, including any direct, indirect, special,
#       incidental, or consequential damages of any character arising as a
#       result of this License or out of the use or inability to use the
#       Work (including but not limited to damages for loss of goodwill,
#       work stoppage, computer failure or malfunction, or any and all
#       other commercial damages or losses), even if such Contributor
#       has been advised of the possibility of such damages.
#
#    9. Accepting Warranty or Additional Liability. While redistributing
#       the Work or Derivative Works thereof, You may choose to offer,
#       and charge a fee for, acceptance of support, warranty, indemnity,
#       or other liability obligations and/or rights consistent with this
#       License. However, in accepting such obligations, You may act only
#       on Your own behalf and on Your sole responsibility, not on behalf
#       of any other Contributor, and only if You agree to indemnify,
#       defend, and hold each Contributor harmless for any liability
#       incurred by, or claims asserted against, such Contributor by reason
#       of your accepting any such warranty or additional liability.
#
#    END OF TERMS AND CONDITIONS
#
#    APPENDIX: How to apply the Apache License to your work.
#
#       To apply the Apache License to your work, attach the following
#       boilerplate notice, with the fields enclosed by brackets "{}"
#       replaced with your own identifying information. (Don't include
#       the brackets!)  The text should be enclosed in the appropriate
#       comment syntax for the file format. We also recommend that a
#       file or class name and description of purpose be included on the
#       same "printed page" as the copyright notice for easier
#       identification within third-party archives.
#
#    Copyright 2017 Gehirn Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# The BPMN-RPA MsGraph library is also based on the msal- and msal-extensions library, which is licensed under the The MIT License (MIT):
# Copyright (c) Microsoft Corporation.
# All rights reserved.
#
# This code is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
