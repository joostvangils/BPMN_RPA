import win32com
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
        Initializes the Outlook class
        """
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

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
        return self.outlook.GetDefaultFolder(folder).Items

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
        return self.outlook.GetDefaultFolder(folder).Items[item].Attachments

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
        inbox = self.get_outlook_folder(6)
        unread_emails = inbox.Items.Restrict("[Unread]=True")
        if mark_as_read:
            for email in unread_emails:
                email.UnRead = False
        return unread_emails

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
        if mark_as_complete:
            for task in tasks:
                task.Complete = True
        return tasks

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
        if mark_as_complete:
            for task in tasks:
                task.Complete = True
        return tasks

    def get_outlook_tomorrow_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for tomorrow
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Tomorrow'")
        if mark_as_complete:
            for task in tasks:
                task.Complete = True
        return tasks

    def get_outlook_this_week_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for this week
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'This Week'")
        if mark_as_complete:
            for task in tasks:
                task.Complete = True
        return tasks

    def get_outlook_next_week_tasks(self, mark_as_complete=True):
        """
        Returns the tasks for next week
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Next Week'")
        if mark_as_complete:
            for task in tasks:
                task.Complete = True
        return tasks

    def get_outlook_overdue_tasks(self, mark_as_complete=True):
        """
        Returns the overdue tasks
        :param mark_as_complete: Optional. Mark the tasks as complete. Default: True.
        :return: Tasks
        """
        tasks = self.outlook.GetDefaultFolder(4).Items.Restrict("[Start] = 'Overdue'")
        if mark_as_complete:
            for task in tasks:
                task.Complete = True
        return tasks

    def get_outlook_completed_tasks(self):
        """
        Returns the completed tasks
        :return: Tasks
        """
        return self.outlook.GetDefaultFolder(4).Items.Restrict("[Complete] = True")

    def get_outlook_incomplete_tasks(self):
        """
        Returns the incomplete tasks
        :return: Tasks
        """
        return self.outlook.GetDefaultFolder(4).Items.Restrict("[Complete] = False")

    def get_outlook_appointments(self):
        """
        Returns the appointments
        :return: Appointments
        """
        return self.outlook.GetDefaultFolder(9).Items

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
        return self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Today'")

    def get_outlook_tomorrow_appointments(self):
        """
        Returns the appointments for tomorrow
        :return: Appointments
        """
        return self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Tomorrow'")

    def get_outlook_this_week_appointments(self):
        """
        Returns the appointments for this week
        :return: Appointments
        """
        return self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'This Week'")

    def get_outlook_next_week_appointments(self):
        """
        Returns the appointments for next week
        :return: Appointments
        """
        return self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Next Week'")

    def get_outlook_overdue_appointments(self):
        """
        Returns the overdue appointments
        :return: Appointments
        """
        return self.outlook.GetDefaultFolder(9).Items.Restrict("[Start] = 'Overdue'")

    def get_outlook_completed_appointments(self):
        """
        Returns the completed appointments
        :return: Appointments
        """
        return self.outlook.GetDefaultFolder(9).Items.Restrict("[Complete] = True")

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




