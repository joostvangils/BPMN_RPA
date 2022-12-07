import json
import pickle

import xmltodict
from pykeepass import PyKeePass


# The BPMN-RPA KeePass module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA KeePass module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA KeePass module is based on the PyKeePass module (copyright Philipp Schmitt) , which is also licensed under the GNU General Public License.

class KeePass:

    def __init__(self, path, master_password):
        self.kp = None
        """
        Opens KeePass
        :param path: Path to the KeePass database
        :param master_password: Master password of the KeePass database
        """
        self.path = path
        self.master_password = master_password
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the KeePass database
        """
        self.kp = PyKeePass(self.path, password=self.master_password)

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

    def keepass_get_password(self, title):
        """
        Returns the password of an entry
        :param title: Title of the entry
        :return: Password
        """
        return self.kp.find_entries(title=title, first=True).password

    def keepass_get_username(self, title):
        """
        Returns the username of an entry
        :param title: Title of the entry
        :return: Username
        """
        return self.kp.find_entries(title=title, first=True).username

    def keepass_get_url(self, title):
        """
        Returns the URL of an entry
        :param title: Title of the entry
        :return: URL
        """
        return self.kp.find_entries(title=title, first=True).url

    def get_notes(self, title):
        """
        Returns the notes of an entry
        :param title: Title of the entry
        :return: Notes
        """
        return self.kp.find_entries(title=title, first=True).notes

    def keepass_get_entry(self, title):
        """
        Returns the entry
        :param title: Title of the entry
        :return: Entry
        """
        return self.kp.find_entries(title=title, first=True)

    def keepass_get_entry_attribute(self, title, attribute):
        """
        Returns an attribute of an entry
        :param title: Title of the entry
        :param attribute: Attribute to return
        :return: Attribute
        """
        return self.kp.find_entries(title=title, first=True)[attribute]

    def keepass_get_entry_attributes(self, title):
        """
        Returns all attributes of an entry
        :param title: Title of the entry
        :return: Attributes
        """
        return self.kp.find_entries(title=title, first=True).__dict__

    def keepass_get_entry_attributes_as_string(self, title):
        """
        Returns all attributes of an entry as a string
        :param title: Title of the entry
        :return: Attributes as string
        """
        return str(self.kp.find_entries(title=title, first=True).__dict__)

    def keepass_get_entry_attributes_as_json(self, title):
        """
        Returns all attributes of an entry as a JSON string
        :param title: Title of the entry
        :return: Attributes as JSON string
        """
        return json.dumps(self.kp.find_entries(title=title, first=True).__dict__)

    def keepass_get_entry_attributes_as_xml(self, title):
        """
        Returns all attributes of an entry as an XML string
        :param title: Title of the entry
        :return: Attributes as XML string
        """
        return xmltodict.unparse(self.kp.find_entries(title=title, first=True).__dict__)

    def keepass_get_entry_attributes_as_dict(self, title):
        """
        Returns all attributes of an entry as a dictionary
        :param title: Title of the entry
        :return: Attributes as dictionary
        """
        return self.kp.find_entries(title=title, first=True).__dict__

    def keepass_get_entry_attributes_as_list(self, title):
        """
        Returns all attributes of an entry as a list
        :param title: Title of the entry
        :return: Attributes as list
        """
        return list(self.kp.find_entries(title=title, first=True).__dict__)

    def keepass_create_entry(self, title, username, password, url, notes):
        """
        Creates an entry
        :param title: Title of the entry
        :param username: Username of the entry
        :param password: Password of the entry
        :param url: URL of the entry
        :param notes: Notes of the entry
        """
        self.kp.add_entry(self.kp.root_group, title, username=username, password=password, url=url, notes=notes)

    def keepass_create_entry_with_attributes(self, title, attributes):
        """
        Creates an entry with attributes
        :param title: Title of the entry
        :param attributes: Attributes of the entry
        """
        self.kp.add_entry(self.kp.root_group, title, **attributes)

    def keepass_delete_entry(self, title):
        """
        Deletes an entry
        :param title: Title of the entry
        """
        self.kp.delete_entry(self.kp.find_entries(title=title, first=True))

    def keepass_update_entry(self, title, username, password, url, notes):
        """
        Updates an entry
        :param title: Title of the entry
        :param username: Username of the entry
        :param password: Password of the entry
        :param url: URL of the entry
        :param notes: Notes of the entry
        """
        entry = self.kp.find_entries(title=title, first=True)
        entry.username = username
        entry.password = password
        entry.url = url
        entry.notes = notes
        entry.save()

    def keepass_update_entry_with_attributes(self, title, attributes):
        """
        Updates an entry with attributes
        :param title: Title of the entry
        :param attributes: Attributes of the entry
        """
        entry = self.kp.find_entries(title=title, first=True)
        for key, value in attributes.items():
            entry[key] = value
        entry.save()

    def keepass_update_entry_attribute(self, title, attribute, value):
        """
        Updates an attribute of an entry
        :param title: Title of the entry
        :param attribute: Attribute to update
        :param value: New value of the attribute
        """
        entry = self.kp.find_entries(title=title, first=True)
        entry[attribute] = value
        entry.save()

    def keepass_save(self):
        """
        Saves the KeePass database
        """
        self.kp.save()

