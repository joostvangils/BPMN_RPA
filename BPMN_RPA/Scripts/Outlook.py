import pickle
import win32com.client


# The BPMN-RPA Outlook module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Outlook module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


class Outlook:

    def __init__(self):
        """
        Initializes the Outlook class.
        On error copy the two files from [installation directory python]\Lib\site-packages\pywin32_system32 to C:\Windows\System32.
        Make sure to run 'python pywin32_postinstall.py -install' from [installation directory python]\Scripts in administrator mode after installing pywin32.
        Then check if you only have one pywintypes.py in your Python subfolders. If not: rename the pywintypes.py in the Python\Lib\site-packages\win32ctypes subfolder to pywintypes_old.py.
        """
        self.outlook = None
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to Desktop Outlook
        """
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    def __is_picklable__(self, obj: any) -> bool:
        """
        Internal function to determine if the object is pickable.
        :param obj: The object to check.
        :return: True or False
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception as e:
            return False

    def __getstate__(self):
        """
        Internal function for serialization
        """
        state = self.__dict__.copy()
        for key, val in state.items():
            if not self.__is_picklable__(val):
                state[key] = str(val)
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def get_outlook_folder(self, folder=6):
        """
        Returns the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :return: Folder
        """
        return self.outlook.GetDefaultFolder(folder)

    def get_outlook_folder_items(self, folder=6):
        """
        Returns the items in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :return: Items
        """
        retn = []
        for item in self.outlook.GetDefaultFolder(folder).Items:
            retn.append(item)
        return retn

    def get_outlook_folder_item(self, folder=6, item=1):
        """
        Returns the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :return: Item
        """
        return self.outlook.GetDefaultFolder(folder).Items[item]

    def get_outlook_folder_item_subject(self, folder=6, item=1):
        """
        Returns the subject of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :return: Subject
        """
        return self.outlook.GetDefaultFolder(folder).Items[item].Subject

    def get_outlook_folder_item_body(self, folder=6, item=1):
        """
        Returns the body of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :return: Body
        """
        return self.outlook.GetDefaultFolder(folder).Items[item].Body

    def get_outlook_folder_item_attachments(self, folder=6, item=1):
        """
        Returns the attachments of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :return: Attachments
        """
        retn = []
        for attachment in self.outlook.GetDefaultFolder(folder).Items[item].Attachments:
            retn.append(attachment)
        return retn

    def get_outlook_folder_item_attachment(self, folder=6, item=1, attachment=1):
        """
        Returns the attachment of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :param attachment: Optional. Attachment to return. Default: First attachment.
        :return: Attachment
        """
        return self.outlook.GetDefaultFolder(folder).Items[item].Attachments[attachment]

    def get_outlook_folder_item_attachment_filename(self, folder=6, item=1, attachment=1):
        """
        Returns the filename of the attachment of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :param attachment: Optional. Attachment to return. Default: First attachment.
        :return: Filename
        """
        return self.outlook.GetDefaultFolder(folder).Items[item].Attachments[attachment].Filename

    def get_outlook_folder_item_attachment_path(self, folder=6, item=1, attachment=1):
        """
        Returns the path of the attachment of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :param attachment: Optional. Attachment to return. Default: First attachment.
        :return: Path
        """
        return self.outlook.GetDefaultFolder(folder).Items[item].Attachments[attachment].Path

    def get_outlook_folder_item_attachment_saveas(self, folder=6, item=1, attachment=1, path=""):
        """
        Saves the attachment of the item in the Outlook folder
        :param folder: Optional. Folder to return. Default: Inbox.
        :param item: Optional. Item to return. Default: First item.
        :param attachment: Optional. Attachment to return. Default: First attachment.
        :param path: Optional. Path to save the attachment. Default: Current folder.
        :return: None
        """
        self.outlook.GetDefaultFolder(folder).Items[item].Attachments[attachment].SaveAsFile(path)

    def get_outlook_unread_emails(self, mark_as_read=True):
        """
        Returns the unread emails
        :param mark_as_read: Optional. Mark the emails as read. Default: True.
        :return: Emails
        """
        retn = []
        inbox = self.get_outlook_folder(6)
        unread_emails = inbox.Items.Restrict("[Unread]=True")
        for email in unread_emails:
            retn.append(email)
            if mark_as_read:
                email.UnRead = False
        return retn

    def create_outlook_folder(self, folder_name):
        """
        Creates a new Outlook folder
        :param folder_name: Name of the new folder
        :return: None
        """
        self.outlook.CreateFolder(folder_name)

    def delete_outlook_folder(self, folder_name):
        """
        Deletes an Outlook folder
        :param folder_name: Name of the folder to delete
        :return: None
        """
        self.outlook.DeleteFolder(folder_name)

    def empty_outlook_folder(self, folder_name):
        """
        Empties an Outlook folder
        :param folder_name: Name of the folder to empty
        :return: None
        """
        self.outlook.EmptyFolder(folder_name)

    def send_outlook_appointment(self, subject, start_date, end_date, location, body, recipients):
        """
        Sends an appointment
        :param subject: Subject of the appointment
        :param start_date: Start date of the appointment
        :param end_date: End date of the appointment
        :param location: Location of the appointment
        :param body: Body of the appointment
        :param recipients: Recipients of the appointment
        :return: None
        """
        appointment = self.outlook.CreateItem(1)
        appointment.Subject = subject
        appointment.Start = start_date
        appointment.End = end_date
        appointment.Location = location
        appointment.Body = body
        appointment.Recipients.Add(recipients)
        appointment.Send()

    def send_outlook_email(self, subject, body, recipients):
        """
        Sends an email
        :param subject: Subject of the email
        :param body: Body of the email
        :param recipients: Recipients of the email
        :return: None
        """
        email = self.outlook.CreateItem(0)
        email.Subject = subject
        email.Body = body
        email.Recipients.Add(recipients)
        email.Send()

    def send_outlook_task(self, subject, body, recipients):
        """
        Sends a task
        :param subject: Subject of the task
        :param body: Body of the task
        :param recipients: Recipients of the task
        :return: None
        """
        task = self.outlook.CreateItem(2)
        task.Subject = subject
        task.Body = body
        task.Recipients.Add(recipients)
        task.Send()

    def get_outlook_tasks(self, mark_as_complete=True):
        """
        Returns the tasks
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        tasks = self.outlook.GetDefaultFolder(4).Items
        retn = []
        for task in tasks:
            retn.append(task)
            if mark_as_complete:
                task.Complete = True
        return retn

    def get_outlook_task(self, task=1, mark_as_complete=True):
        """
        Returns the task
        :param task: Optional. Task to return. Default: First task.
        :param mark_as_complete: Optional. Mark the task as complete. Default: True.
        :return: Task
        """
        task = self.outlook.GetDefaultFolder(4).Items[task]
        if mark_as_complete:
            task.Complete = True
        return task

    def get_outlook_today_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for today
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Today'")
        retn = []
        for task in tasks:
            retn.append(task)
            if mark_as_complete:
                task.Complete = True
        return retn

    def get_outlook_tomorrow_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for tomorrow
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        retn = []
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Tomorrow'")
        for task in tasks:
            retn.append(task)
            if mark_as_complete:
                task.Complete = True
        return retn

    def get_outlook_this_week_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for this week
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        retn = []
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'This Week'")
        for task in tasks:
            retn.append(task)
            if mark_as_complete:
                task.Complete = True
        return retn

    def get_outlook_next_week_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for next week
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        retn = []
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Next Week'")
        for task in tasks:
            retn.append(task)
            if mark_as_complete:
                task.Complete = True
        return retn

    def get_outlook_overdue_tasks(self, mark_as_complete=True):
        """
        Returns the overdue tasks
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        retn = []
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Overdue'")
        for task in tasks:
            retn.append(task)
            if mark_as_complete:
                task.Complete = True
        return retn

    def get_outlook_completed_tasks(self):
        """
        Returns the completed tasks
        :return: Tasks
        """
        retn = []
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Complete] = True")
        for task in tasks:
            retn.append(task)
        return retn

    def get_outlook_incomplete_tasks(self):
        """
        Returns the incomplete tasks
        :return: Tasks
        """
        retn = []
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Complete] = False")
        for task in tasks:
            retn.append(task)
        return retn

    def get_outlook_appointments(self):
        """
        Returns the appointments
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def get_outlook_appointment(self, appointment=1):
        """
        Returns the appointment
        :param appointment: Optional. Appointment to return. Default: First appointment.
        :return: Appointment
        """
        return self.outlook.GetDefaultFolder(9).Items[appointment]

    def get_outlook_today_appointments(self):
        """
        Returns the appointments for today
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Today'")
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def get_outlook_tomorrow_appointments(self):
        """
        Returns the appointments for tomorrow
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Tomorrow'")
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def get_outlook_this_week_appointments(self):
        """
        Returns the appointments for this week
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'This Week'")
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def get_outlook_next_week_appointments(self):
        """
        Returns the appointments for next week
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Next Week'")
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def get_outlook_overdue_appointments(self):
        """
       Returns the overdue appointments
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Overdue'")
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def get_outlook_completed_appointments(self):
        """
        Returns the completed appointments
        :return: Appointments
        """
        retn = []
        appointments = self.outlook.GetDefaultFolder(9).Items.Restrict("[Complete] = True")
        for appointment in appointments:
            retn.append(appointment)
        return retn

    def create_outlook_appointment_out_of_office(self, subject, body, recipients, start, end):
        """
        Creates an appointment that idicates you are out of office
        :param subject: Subject
        :param body: Body
        :param recipients: Recipients
        :param start: Start
        :param end: End
        :return: None
        """
        appointment = self.outlook.CreateItem(1)
        appointment.Subject = subject
        appointment.Body = body
        appointment.Recipients.Add(recipients)
        appointment.Start = start
        appointment.End = end
        appointment.BusyStatus = 3
        appointment.Save()

    def get_outlook_current_availability_of_person(self, person):
        """
        Returns the availability of a person
        :param person: Person to check
        :return: Availability
        """
        return self.outlook.Session.GetFolderFromID(person).FreeBusyStatus

    def get_outlook_availability_of_person_on_datetime_range(self, person, start_datetime, end_datetime):
        """
        Returns the availability of a person on a datetime range
        :param person: Person to check
        :param start_datetime: Start datetime to check
        :param end_datetime: End datetime to check
        :return: Availability
        """
        return self.outlook.Session.GetFolderFromID(person).GetFreeBusy(start_datetime, end_datetime, 60)

    def get_outlook_availability_of_person_on_datetime_range_with_interval(self, person, start_datetime, end_datetime, interval):
        """
        Returns the availability of a person on a datetime range with interval
        :param person: Person to check
        :param start_datetime: Start datetime to check
        :param end_datetime: End datetime to check
        :param interval: Interval to check
        :return: Availability
        """
        return self.outlook.Session.GetFolderFromID(person).GetFreeBusy(start_datetime, end_datetime, interval)

    def get_outlook_availability_of_person_on_datetime_range_with_interval_and_details(self, person, start_datetime, end_datetime, interval, details):
        """
        Returns the availability of a person on a datetime range with interval and details
        :param person: Person to check
        :param start_datetime: Start datetime to check
        :param end_datetime: End datetime to check
        :param interval: Interval to check
        :param details: Details to check
        :return: Availability
        """
        return self.outlook.Session.GetFolderFromID(person).GetFreeBusy(start_datetime, end_datetime, interval, details)

    def empty_outlook_trash(self):
        """
        Empties the Outlook trash
        """
        self.outlook.GetDefaultFolder(3).Items.Delete()
