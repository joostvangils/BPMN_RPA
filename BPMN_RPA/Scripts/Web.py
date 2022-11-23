import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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
class Web:

    def __init__(self, url=""):
        """
        Instantiate class for reading web pages
        :param url: The url of the page to open
        """
        self.downloaddir = r"\temp"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": self.downloaddir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.url = url
        self.soup = None
        if self.url != "":
            self.driver.get(self.url)
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def get_text_by_id(self, id):
        """
        Get the text of a html element of the page by its ID.
        :param id: The ID of the html element
        :return: The text of the html element
        """
        return self.soup.find(id=id).text

    def get_text_by_classname(self, htmltag, class_name, number=1):
        """
        Get the text of a html element by its classname.
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

    def get_text_by_tag(self, htmltag, number=1):
        """
        Get the text of a html element by its tag.
        :param htmltag: The tagname of the html element
        :param number: Optional. Retreive the text from the n-th element of the elements with the same tag
        :return: The text of the html element
        """
        all = self.soup.find_all(htmltag)
        count = 1
        retn = None
        for el in all:
            if count == number:
                retn = el
                break
            count += 1
        return retn.text

    def get_text_by_tag_and_classname(self, htmltag, class_name, number=1):
        """
        Get the text of a html element by its tag and classname.
        :param htmltag: The tagname of the html element
        :param class_name: The classname of the html element
        :param number: Optional. Retreive the text from the n-th element of the elements with the same tag and classname
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

    def get_text_by_tag_and_id(self, htmltag, element_id, number=1):
        """
        Get the text of a html element by its tag and id.
        :param htmltag: The tagname of the html element
        :param element_id: The id of the html element
        :param number: Optional. Retreive the text from the n-th element of the elements with the same tag and id
        :return: The text of the html element
        """
        all = self.soup.find_all(htmltag, id=element_id)
        count = 1
        retn = None
        for el in all:
            if count == number:
                retn = el
                break
            count += 1
        return retn.text

    def get_text_by_tag_and_attribute(self, htmltag, attribute, value, number=1):
        """
        Get the text of a html element by its tag and attribute.
        :param htmltag: The tagname of the html element
        :param attribute: The attribute of the html element
        :param value: The value of the attribute
        :param number: Optional. Retreive the text from the n-th element of the elements with the same tag and attribute
        :return: The text of the html element
        """
        all = self.soup.find_all(htmltag, {attribute: value})
        count = 1
        retn = None
        for el in all:
            if count == number:
                retn = el
                break
            count += 1
        return retn.text

    def get_text_by_tag_and_attribute_and_classname(self, htmltag, attribute, value, class_name, number=1):
        """
        Get the text of a html element by its tag, attribute and classname.
        :param htmltag: The tagname of the html element
        :param attribute: The attribute of the html element
        :param value: The value of the attribute
        :param class_name: The classname of the html element
        :param number: Optional. Retreive the text from the n-th element of the elements with the same tag, attribute and classname
        :return: The text of the html element
        """
        all = self.soup.find_all(htmltag, {attribute: value}, class_=class_name)
        count = 1
        retn = None
        for el in all:
            if count == number:
                retn = el
                break
            count += 1
        return retn.text

    def get_text_by_tag_and_attribute_and_id(self, htmltag, attribute, value, element_id, number=1):
        """
        Get the text of a html element by its tag, attribute and id.
        :param htmltag: The tagname of the html element
        :param attribute: The attribute of the html element
        :param value: The value of the attribute
        :param element_id: The id of the html element
        :param number: Optional. Retreive the text from the n-th element of the elements with the same tag, attribute and id
        :return: The text of the html element
        """
        all = self.soup.find_all(htmltag, {attribute: value}, id=element_id)
        count = 1
        retn = None
        for el in all:
            if count == number:
                retn = el
                break
            count += 1
        return retn.text

    def get_image_by_id(self, element_id):
        """
        Get the image of a html element by its id.
        :param element_id: The id of the html element
        :return: The source url of the image of the html element
        """
        return self.soup.find(id=element_id).img['src']

    def click_link_by_id(self, element_id):
        """
        Click a link by its id.
        :param element_id: The id of the link
        """
        self.driver.find_element(By.ID, element_id).click()

    def click_link_with_text(self, text):
        """
        Click a link by its text.
        :param text: The text of the link
        """
        self.driver.find_element(By.LINK_TEXT, text).click()

    def click_link_by_classname(self, class_name):
        """
        Click a link by its classname.
        :param class_name: The classname of the link
        """
        self.driver.find_element(By.CLASS_NAME, class_name).click()

    def click_button_with_text(self, text):
        """
        Click a button by its text.
        :param text: The text of the button
        """
        self.driver.find_element(By.XPATH, "//button[contains(text(), '" + text + "')]").click()

    def click_button_by_id(self, element_id):
        """
        Click a button by its id.
        :param element_id: The id of the button
        """
        self.driver.find_element(By.ID, element_id).click()

    def click_button_by_classname(self, class_name, index=0):
        """
        Click a button by its classname.
        :param class_name: The classname of the button
        :param index: Optional. Click the n-th button with the same classname
        """
        self.driver.find_elements(By.CLASS_NAME, class_name)[index].click()

    def click_button_by_attribute(self, attribute, value):
        """
        Click a button by its attribute.
        :param attribute: The attribute of the button
        :param value: The value of the attribute
        """
        self.driver.find_element(By.XPATH, "//button[@" + attribute + "='" + value + "']").click()

    def set_textfield_with_label(self, with_textlabel, text):
        """
        Set the text of a textfield by its label.
        :param with_textlabel: The label of the textfield
        :param text: The text to set
        """
        self.driver.find_element(By.XPATH, "//label[contains(text(), '" + with_textlabel + "')]/following-sibling::input").send_keys(text)

    def set_textfield_by_id(self, element_id, text):
        """
        Set the text of a textfield by its id.
        :param element_id: The id of the textfield
        :param text: The text to set
        """
        self.driver.find_element(By.ID, element_id).send_keys(text)

    def set_textfield_by_classname(self, class_name, text, index=0):
        """
        Set the text of a textfield by its classname.
        :param class_name: The classname of the textfield
        :param text: The text to set
        :param index: Optional. Set the text of the n-th textfield with the same classname
        """
        self.driver.find_elements(By.CLASS_NAME, class_name)[index].send_keys(text)

    def set_textfield_by_xpath(self, xpath, text):
        """
        Set the text of a textfield by its xpath.
        :param xpath: The xpath of the textfield
        :param text: The text to set
        """
        self.driver.find_element(By.XPATH, xpath).send_keys(text)

    def set_textfield_by_attribute(self, attribute, value, text):
        """
        Set the text of a textfield by its attribute.
        :param attribute: The attribute of the textfield
        :param value: The value of the attribute
        :param text: The text to set
        """
        self.driver.find_element(By.XPATH, "//input[@" + attribute + "='" + value + "']").send_keys(text)

    def set_option_by_label(self, with_textlabel, option):
        """
        Set the option of a select by its label.
        :param with_textlabel: The label of the select
        :param option: The option to set
        """
        self.driver.find_element(By.XPATH, "//label[contains(text(), '" + with_textlabel + "')]/following-sibling::select").send_keys(option)

    def set_option_by_id(self, element_id, option):
        """
        Set the option of a select by its id.
        :param element_id: The id of the select
        :param option: The option to set
        """
        self.driver.find_element(By.ID, element_id).send_keys(option)

    def select_combobox_by_label(self, with_textlabel, option):
        """
        Select an option of a combobox by its label.
        :param with_textlabel: The label of the combobox
        :param option: The option to select
        """
        self.driver.find_element(By.XPATH, "//label[contains(text(), '" + with_textlabel + "')]/following-sibling::div").click()
        self.driver.find_element(By.XPATH, "//label[contains(text(), '" + with_textlabel + "')]/following-sibling::div//li[contains(text(), '" + option + "')]").click()

    def select_combobox_by_id(self, element_id, option):
        """
        Select an option of a combobox by its id.
        :param element_id: The id of the combobox
        :param option: The option to select
        """
        self.driver.find_element(By.ID, element_id).click()
        self.driver.find_element(By.XPATH, "//div[@id='" + element_id + "']//li[contains(text(), '" + option + "')]").click()

    def select_combobox_by_classname(self, class_name, option, index=0):
        """
        Select an option of a combobox by its classname.
        :param class_name: The classname of the combobox
        :param option: The option to select
        :param index: The index of the combobox
        """
        self.driver.find_elements(By.CLASS_NAME, class_name)[index].click()
        self.driver.find_elements(By.XPATH, "//div[@class='" + class_name + "'][" + str(index) + "]//li[contains(text(), '" + option + "')]").click()

    def select_combobox_by_attribute(self, attribute, value, option):
        """
        Select an option of a combobox by its attribute.
        :param attribute: The attribute of the combobox
        :param value: The value of the attribute
        :param option: The option to select
        """
        self.driver.find_element(By.XPATH, "//div[@" + attribute + "='" + value + "']").click()
        self.driver.find_element(By.XPATH, "//div[@" + attribute + "='" + value + "']//li[contains(text(), '" + option + "')]").click()

    def select_checkbox_by_label(self, with_textlabel, index=0):
        """
        Select a checkbox by its label.
        :param with_textlabel: The label of the checkbox
        :param index: The index of the checkbox
        """
        self.driver.find_elements(By.XPATH, "//label[contains(text(), '" + with_textlabel + "')]/preceding-sibling::input")[index].click()

    def select_checkbox_by_id(self, element_id):
        """
        Select a checkbox by its id.
        :param element_id: The id of the checkbox
        """
        self.driver.find_element(By.ID, element_id).click()

    def select_checkbox_by_xpath(self, xpath):
        """
        Select a checkbox by its xpath.
        :param xpath: The xpath of the checkbox
        """
        self.driver.find_element(By.XPATH, xpath).click()

    def select_checkbox_by_classname(self, class_name, index=0):
        """
        Select a checkbox by its classname.
        :param class_name: The classname of the checkbox
        :param index: The index of the checkbox
        """
        self.driver.find_elements(By.CLASS_NAME, class_name)[index].click()

    def select_checkbox_by_attribute(self, attribute, value):
        """
        Select a checkbox by its attribute.
        :param attribute: The attribute of the checkbox
        :param value: The value of the attribute
        """
        self.driver.find_element(By.XPATH, "//input[@" + attribute + "='" + value + "']").click()

    def direct_download_file(self, url):
        """
        Download a file directly from a url.
        :param url: The url of the file
        """
        self.driver.get(url)

    def wait_until_element_is_visible(self, element):
        """
        Wait until an element is visible.
        :param element: The element to wait for
        """
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, element)))

    def wait_until_element_is_clickable(self, element):
        """
        Wait until an element is clickable.
        :param element: The element to wait for
        """
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, element)))

    def wait_until_element_is_invisible(self, element):
        """
        Wait until an element is invisible.
        :param element: The element to wait for
        """
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.XPATH, element)))

    def wait_until_element_is_not_present(self, element):
        """
        Wait until an element is not present.
        :param element: The element to wait for
        """
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, element)))

    def wait_until_text_is_present(self, element, text):
        """
        Wait until a text is present.
        :param element: The element to wait for
        :param text: The text to wait for
        """
        WebDriverWait(self.driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, element), text))

    def wait_until_text_is_not_present(self, element, text):
        """
        Wait until a text is not present.
        :param element: The element to wait for
        :param text: The text to wait for
        """
        WebDriverWait(self.driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, element), text))

    def wait_until_page_is_loaded(self):
        """
        Wait until the page is loaded.
        """
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))

    def save_page_html(self, path):
        """
        Save the page html.
        :param path: The path to save the html
        """
        with open(path, 'w') as f:
            f.write(self.driver.page_source)

    def save_page_screenshot(self, path):
        """
        Save the page screenshot.
        :param path: The path to save the screenshot
        """
        self.driver.save_screenshot(path)

    def get_all_readable_text(self):
        """
        Get all readable text from the page.
        :return: The readable text
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup.get_text()

    def page_contains_text(self, text):
        """
        Check if the page contains a text.
        :param text: The text to check
        :return: True if the page contains the text, False otherwise
        """
        return text in self.get_all_readable_text()

    def get_all_links(self):
        """
        Get all links from the page.
        :return: The links
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True)]

    def page_contains_link(self, link):
        """
        Check if the page contains a link.
        :param link: The link to check
        :return: True if the page contains the link, False otherwise
        """
        return link in self.get_all_links()

    def get_all_images(self):
        """
        Get all source urls of images on the page.
        :return: The source urls of the images
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return [img['src'] for img in soup.find_all('img', src=True)]

    def click_element_in_shadow_root_by_selector(self, shadow_root_parent_id, selector_path):
        """
        Click an element in a shadow root by its text.
        :param shadow_root_parent_id: The id of the shadow root parent
        :param selector_path: The selector path of the element. You can get this path by opening developer mode of the browser, finding the element and then right-click on it and select 'Copy > Copy selector'.
        """
        try:
            ctr = self.driver.find_element(By.ID, shadow_root_parent_id)
            shadow_root = ctr.shadow_root
            element = shadow_root.find_element(By.CSS_SELECTOR, selector_path)
            element.click()
        except Exception as e:
            print(e)

    def click_button_by_xpath(self, xpath):
        """
        Click a button by its xpath.
        :param xpath: The xpath of the button
        """
        self.driver.find_element(By.XPATH, xpath).click()

    def wait_until_button_is_clickable_by_xpath(self, xpath):
        """
        Wait until a button is clickable by its xpath.
        :param xpath: The xpath of the button
        """
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def set_combo_box_value_by_xpath(self, xpath, value):
        """
        Set a value of a combo box by its xpath.
        :param xpath: The xpath of the combo box
        :param value: The value to set
        """
        self.driver.find_element(By.XPATH, xpath).send_keys(value)
