import pickle

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
#
# The BPMN-RPA System module uses the BeautifulSoup4 library, which is licensed under the creative commons license:
# © 1996-2022 Leonard Richardson.
# You are free to:
# Share — copy and redistribute the material in any medium or format
# Adapt — remix, transform, and build upon the material
# for any purpose, even commercially.
# This license is acceptable for Free Cultural Works.
# The licensor cannot revoke these freedoms as long as you follow the license terms.
# Under the following terms:
# Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
# ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.
# No additional restrictions — You may not apply legal terms or technological measures
# that legally restrict others from doing anything the license permits.
# Notices:
# You do not have to comply with the license for elements of the material in the public domain or where your use is permitted by an applicable exception or limitation.
# No warranties are given. The license may not give you all of the permissions necessary for your intended use.
# For example, other rights such as publicity, privacy, or moral rights may limit how you use the material.
#
# The BPMN-RPA System module uses the Selenium library, which is licensed under the Apache License 2.0:
# Please look here for copyright and attributions: https://www.selenium.dev/documentation/about/copyright/
# Apache License
# Version 2.0, January 2004
# http://www.apache.org/licenses/
# TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
# 1. Definitions.
# "License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.
# "Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.
# "Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity.
# For the purposes of this definition, "control" means (i) the power, direct or indirect, to cause the direction or management of such entity,
# whether by contract or otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding shares, or (iii) beneficial ownership of such entity.
# "You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.
# "Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.
# "Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code,
# generated documentation, and conversions to other media types.
# "Work" shall mean the work of authorship, whether in Source or Object form, made available under the License, as indicated by a copyright notice that is included
# in or attached to the work (an example is provided in the Appendix below).
# "Derivative Works" shall mean any work, whether in Source or Object form, that is based on (or derived from) the Work and for which the editorial revisions,
# annotations, elaborations, or other modifications represent, as a whole, an original work of authorship. For the purposes of this License, Derivative Works shall
# not include works that remain separable from, or merely link (or bind by name) to the interfaces of, the Work and Derivative Works thereof.
# "Contribution" shall mean any work of authorship, including the original version of the Work and any modifications or additions to that Work or Derivative Works thereof,
# that is intentionally submitted to Licensor for inclusion in the Work by the copyright owner or by an individual or Legal Entity authorized to submit on behalf of
# the copyright owner. For the purposes of this definition, "submitted" means any form of electronic, verbal, or written communication sent to the Licensor or
# its representatives, including but not limited to communication on electronic mailing lists, source code control systems, and issue tracking systems that are managed by,
# or on behalf of, the Licensor for the purpose of discussing and improving the Work, but excluding communication that is conspicuously marked or otherwise designated
# in writing by the copyright owner as "Not a Contribution."
# "Contributor" shall mean Licensor and any individual or Legal Entity on behalf of whom a Contribution has been received by Licensor and subsequently
# incorporated within the Work.
# 2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide,
# non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense,
# and distribute the Work and such Derivative Works in Source or Object form.
# 3. Grant of Patent License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge,
# royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work,
# where such license applies only to those patent claims licensable by such Contributor that are necessarily infringed by their Contribution(s) alone or by combination
# of their Contribution(s) with the Work to which such Contribution(s) was submitted. If You institute patent litigation against any entity (including a cross-claim or
# counterclaim in a lawsuit) alleging that the Work or a Contribution incorporated within the Work constitutes direct or contributory patent infringement, then any patent
# licenses granted to You under this License for that Work shall terminate as of the date such litigation is filed.
# 4. Redistribution. You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object
# form, provided that You meet the following conditions:
# You must give any other recipients of the Work or Derivative Works a copy of this License; and
# You must cause any modified files to carry prominent notices stating that You changed the files; and
# You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work,
# excluding those notices that do not pertain to any part of the Derivative Works; and
# If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices
# contained within such NOTICE file, excluding those notices that do not pertain to any part of the Derivative Works, in at least one of the following places: within a NOTICE
# text file distributed as part of the Derivative Works; within the Source form or documentation, if provided along with the Derivative Works; or, within a display generated
# by the Derivative Works, if and wherever such third-party notices normally appear. The contents of the NOTICE file are for informational purposes only and do not modify the
# License. You may add Your own attribution notices within Derivative Works that You distribute, alongside or as an addendum to the NOTICE text from the Work, provided that
# such additional attribution notices cannot be construed as modifying the License.
# You may add Your own copyright statement to Your modifications and may provide additional or different license terms and conditions for use, reproduction, or distribution of
# Your modifications, or for any such Derivative Works as a whole, provided Your use, reproduction, and distribution of the Work otherwise complies with the conditions stated
# in this License.
# 5. Submission of Contributions. Unless You explicitly state otherwise, any Contribution intentionally submitted for inclusion in the Work by You to the Licensor shall be
# under the terms and conditions of this License, without any additional terms or conditions. Notwithstanding the above, nothing herein shall supersede or modify the terms of
# any separate license agreement you may have executed with Licensor regarding such Contributions.
# 6. Trademarks. This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable
# and customary use in describing the origin of the Work and reproducing the content of the NOTICE file.
# 7. Disclaimer of Warranty. Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE,
# NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the
# Work and assume any risks associated with Your exercise of permissions under this License.
# 8. Limitation of Liability. In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable
# law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Contributor be liable to You for damages, including any direct, indirect, special,
# incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work (including but not limited to
# damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), even if such Contributor has been
# advised of the possibility of such damages.
# 9. Accepting Warranty or Additional Liability. While redistributing the Work or Derivative Works thereof, You may choose to offer, and charge a fee for, acceptance
# of support, warranty, indemnity, or other liability obligations and/or rights consistent with this License. However, in accepting such obligations, You may act only
# on Your own behalf and on Your sole responsibility, not on behalf of any other Contributor, and only if You agree to indemnify, defend, and hold each Contributor harmless
# for any liability incurred by, or claims asserted against, such Contributor by reason of your accepting any such warranty or additional liability.
# END OF TERMS AND CONDITIONS


class Web:

    def __init__(self, url=""):
        """
        Instantiate class for reading web pages. To make this work, you should install the Selenium Chrome driver and
        add it to your PATH. See https://sites.google.com/a/chromium.org/chromedriver/downloads for more information.
        :param url: The url of the page to open
        """
        self.downloaddir = r"\temp"
        self.url = url
        self.soup = None
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the web page
        :return: None
        """
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": self.downloaddir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        if self.url != "":
            self.driver.get(self.url)
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

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
        self.driver.quit()
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

    def close(self):
        """
        Close the browser.
        """
        self.driver.quit()

    def set_textfield_by_name(self, field_name, value):
        """
        Set a value of a text field by its name.
        :param field_name: The name of the text field
        :param value: The value to set
        """
        self.driver.find_element(By.NAME, field_name).send_keys(value)