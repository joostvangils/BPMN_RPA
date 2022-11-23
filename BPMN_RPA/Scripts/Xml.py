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

class Xml:

    def __init__(self, xml_file):
        """
        Opens an XML file and initializes the class for later use
        :param xml_file:
        """
        self.xml_file = xml_file
        self.xml_dict = xmltodict.parse(open(self.xml_file).read())

    def get_xml_dictionary(self):
        """
        Reads an XML file into a dictionary
        :return: Dictionary
        """
        self.xml_dict = xmltodict.parse(open(self.xml_file).read())
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

    def remove_xml_element(self,  element):
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
