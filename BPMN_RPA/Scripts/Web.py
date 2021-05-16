import requests
from bs4 import BeautifulSoup


class Web:
    # The BPMN-RPA System module is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # The BPMN-RPA System module is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <https://www.gnu.org/licenses/>.

    def __init__(self, url):
        """
        Instantiate class for reading web pages
        :param url: The url of the page to read
        """
        self.url = url
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def get_text_by_id(self, id):
        """
        Get the text of a html element of the page by it's ID.
        :param id: The ID of the html element
        :return: The text of the html element
        """
        return self.soup.find(id=id).text

    def get_text_by_classname(self, htmltag, class_name, number=1):
        """
        Get the text of a html element by it's classname.
        :param htmltag: The tagname of the html element
        :param class_name: The classname of the html element
        :param number: Optional. Retreive the text from the n-th element of the elements with the same classname
        :return: The text of the html element
        """
        all = self.soup.find_all(htmltag, class_=class_name)
        count = 1
        retn = None
        for el in all:
            if count == number:
                retn = el
                break
            count += 1
        return retn.text