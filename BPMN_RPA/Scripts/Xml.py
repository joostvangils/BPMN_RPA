import pickle

import xmltodict


# The BPMN-RPA XML module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA XML module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA XML module is also based on the xmltodict library, which is licensed under the MIT License:
# Copyright (C) 2012 Martin Blech and individual contributors.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


class Xml:

    def __init__(self, xml_file):
        """
        Opens an XML file and initializes the class for later use
        :param xml_file:
        """
        self.xml_file = xml_file
        self.xml_dict = None
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect the XML file to the dictionary
        """
        with open(self.xml_file, 'r') as f:
            self.xml_dict = xmltodict.parse(f.read())

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

    def get_xml_dictionary(self):
        """
        Reads an XML file into a dictionary
        :return: Dictionary
        """
        with open(self.xml_file, 'r') as f:
            self.xml_dict = xmltodict.parse(f.read())
        return self.xml_dict

    def write_xml_file(self, xml_file):
        """
        Writes a dictionary to an XML file
        :param xml_file: XML file to write
        """
        with open(xml_file, 'w') as f:
            f.write(xmltodict.unparse(self.xml_dict))

    def get_xml_element(self, element):
        """
        Returns the element from the dictionary
        :param element: Element to return
        :return: Element
        """
        return self.xml_dict[element]

    def add_xml_element(self, element, element_dict):
        """
        Adds an element to the dictionary

        :param element: Element to add
        :param element_dict: Element dictionary to add
        """
        self.xml_dict[element] = element_dict

    def remove_xml_element(self, element):
        """
        Removes the element from the dictionary
        :param element: Element to remove
        """
        self.xml_dict.pop(element)

    def get_xml_element_attribute(self, element, attribute):
        """
        Returns the attribute from the element
        :param element: Element to search
        :param attribute: Attribute to return
        :return: Attribute
        """
        return self.xml_dict[element][attribute]

    def set_xml_element_attribute(self, element, attribute, value):
        """
        Sets the attribute of the element
        :param element: Element to search
        :param attribute: Attribute to set
        :param value: Value to set
        """
        self.xml_dict[element][attribute] = value

    def get_xml_element_text(self, xml_dict, element):
        """
        Returns the text from the element
        :param xml_dict: Dictionary to search
        :param element: Element to search
        :return: Text
        """
        return xml_dict[element]['#text']

    def set_xml_element_text(self, element, text):
        """
        Sets the text of the element
        :param element: Element to search
        :param text: Text to set
        """
        self.xml_dict[element]['#text'] = text

    def get_xml_element_children(self, element):
        """
        Returns the children of the element
        :param element: Element to search
        :return: Children
        """
        return self.xml_dict[element]['children']

    def get_xml_element_child(self, element, child):
        """
        Returns the child of the element
        :param xml_dict: Dictionary to search
        :param element: Element to search
        :param child: Child to return
        :return: Child
        """
        return self.xml_dict[element]['children'][child]

    def get_xml_element_child_attribute(self, element, child, attribute):
        """
        Returns the attribute from the child of the element
        :param element: Element to search
        :param child: Child to search
        :param attribute: Attribute to return
        :return: Attribute
        """
        return self.xml_dict[element]['children'][child][attribute]

    def set_xml_element_child_attribute(self, element, child, attribute, value):
        """
        Sets the attribute of the child of the element
        :param element: Element to search
        :param child: Child to search
        :param attribute: Attribute to set
        :param value: Value to set
        """
        self.xml_dict[element]['children'][child][attribute] = value

    def get_xml_element_child_text(self, element, child):
        """
        Returns the text from the child of the element
        :param element: Element to search
        :param child: Child to search
        :return: Text
        """
        return self.xml_dict[element]['children'][child]['#text']

    def add_xml_element_child(self, element, child, child_dict):
        """
        Adds a child to the element
        :param element: Element to search
        :param child: Child to add
        :param child_dict: Child dictionary to add
        """
        self.xml_dict[element]['children'].append({child: child_dict})

    def set_xml_element_child_text(self, element, child, text):
        """
        Sets the text of the child of the element
        :param element: Element to search
        :param child: Child to search
        :param text: Text to set
        """
        self.xml_dict[element]['children'][child]['#text'] = text

    def remove_xml_element_child(self, element, child):
        """
        Removes the child from the element
        :param element: Element to search
        :param child: Child to remove
        """
        self.xml_dict[element]['children'].pop(child)
