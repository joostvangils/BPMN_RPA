import json
import os
import pickle

import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter


# The BPMN-RPA PDF module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA PDF module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA PDF module is based on the PyPDF2 module (copyright Mathieu Fenniak) , which is licensed under the BSD License:
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# All advertising materials mentioning features or use of this software must display the following acknowledgement: This product includes software developed by the <copyright holder>.
# Neither the name of the <copyright holder> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class PDF:

    def __init__(self, pdf_file_path):
        """
        Opens the PDF file and initializes the PDF class that references the pdf for other functions
        :param pdf_file_path:
        """
        self.pdf_file_path = pdf_file_path
        self.pdf_file = None
        self.pdf_reader = None
        self.pdf_writer = None
        self.pages = None
        self.page = None
        self.page_content = None
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the PDF
        """
        self.pdf_file = open(self.pdf_file_path, 'rb')
        self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file)
        self.pdf_writer = PyPDF2.PdfFileWriter()
        self.pages = self.pdf_reader.getNumPages()
        self.page = self.pdf_reader.getPage(0)
        self.page_content = self.page.extractText()

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

    def get_page_content(self, page_number):
        """
        Returns the content of a page as a string
        :param page_number: The page number to get the content of
        """
        page = self.pdf_reader.getPage(page_number)
        return page.extractText()

    def get_page_count(self):
        """
        Returns the number of pages in the PDF
        :return: The number of pages in the PDF
        """
        return self.pages

    def get_image_count(self):
        """
        Returns the number of images in the PDF
        :return: The number of images in the PDF
        """
        return len(self.page['/Resources']['/XObject'].getObject())

    def get_image(self, image_number):
        """
        Returns the image from the PDF
        :param image_number: The image number to get
        :return: The image from the PDF
        """
        return self.page['/Resources']['/XObject'].getObject()[image_number]

    def get_image_names(self):
        """
        Returns the names of the images in the PDF
        :return: The names of the images in the PDF
        """
        return self.page['/Resources']['/XObject'].getObject().keys()

    def get_image_names_and_numbers(self):
        """
        Returns the names and numbers of the images in the PDF
        :return: The names and numbers of the images in the PDF
        """
        return self.page['/Resources']['/XObject'].getObject().items()

    def get_image_names_and_numbers_as_dict(self):
        """
        Returns the names and numbers of the images in the PDF as a dictionary
        :return: The names and numbers of the images in the PDF as a dictionary
        """
        return dict(self.page['/Resources']['/XObject'].getObject().items())

    def get_image_names_and_numbers_as_list(self):
        """
        Returns the names and numbers of the images in the PDF as a list
        :return: The names and numbers of the images in the PDF as a list
        """
        return list(self.page['/Resources']['/XObject'].getObject().items())

    def get_image_names_as_list(self):
        """
        Returns the names of the images in the PDF as a list
        :return: The names of the images in the PDF as a list
        """
        return list(self.page['/Resources']['/XObject'].getObject().keys())

    def get_image_names_as_dict(self):
        """
        Returns the names of the images in the PDF as a dictionary
        :return: The names of the images in the PDF as a dictionary
        """
        return dict(self.page['/Resources']['/XObject'].getObject().keys())

    def get_image_numbers_as_list(self):
        """
        Returns the numbers of the images in the PDF as a list
        :return: The numbers of the images in the PDF as a list
        """
        return list(self.page['/Resources']['/XObject'].getObject().values())

    def get_image_numbers_as_dict(self):
        """
        Returns the numbers of the images in the PDF as a dictionary
        :return: The numbers of the images in the PDF as a dictionary
        """
        return dict(self.page['/Resources']['/XObject'].getObject().values())

    def get_image_numbers(self):
        """
        Returns the numbers of the images in the PDF
        :return: The numbers of the images in the PDF
        """
        return self.page['/Resources']['/XObject'].getObject().values()

    def save_pdf(self, file_path):
        """
        Saves the PDF as a new file
        :param file_path: The file path to save the PDF
        """
        with open(file_path, 'wb') as f:
            self.pdf_writer.write(f)

    def get_text_from_page(self, page_number):
        """
        Returns the text from a page
        :param page_number: The page number to get the text from
        :return: The text from a page
        """
        return self.pdf_reader.getPage(page_number).extractText()

    def get_text_from_all_pages(self):
        """
        Returns the text from all pages
        :return: The text from all pages
        """
        text = ""
        for page in range(self.pages):
            text += self.pdf_reader.getPage(page).extractText()
        return text

    def get_text_from_all_pages_as_list(self):
        """
        Returns the text from all pages as a list
        :return: The text from all pages as a list
        """
        text = []
        for page in range(self.pages):
            text.append(self.pdf_reader.getPage(page).extractText())
        return text

    def get_text_from_all_pages_as_dict(self):
        """
        Returns the text from all pages as a dictionary
        :return: The text from all pages as a dictionary
        """
        text = {}
        for page in range(self.pages):
            text[page] = self.pdf_reader.getPage(page).extractText()
        return text

    def get_text_from_all_pages_as_list_of_dicts(self):
        """
        Returns the text from all pages as a list of dictionaries
        :return: The text from all pages as a list of dictionaries
        """
        text = []
        for page in range(self.pages):
            text.append({page: self.pdf_reader.getPage(page).extractText()})
        return text

    def get_text_from_all_pages_as_dict_of_lists(self):
        """
        Returns the text from all pages as a dictionary of lists
        :return: The text from all pages as a dictionary of lists
        """
        text = {}
        for page in range(self.pages):
            text[page] = [self.pdf_reader.getPage(page).extractText()]
        return text

    def annotate_page(self, page_number, annotation):
        """
        Annotates a page
        :param page_number: The page number to annotate
        :param annotation: The annotation to add
        """
        self.pdf_reader.getPage(page_number).annotations.insert(0, annotation)

    def split_pdf(self, file_path):
        """
        Splits the PDF into individual pages
        :param file_path: The file path to save the PDF
        """
        self.pdf_file_path = file_path
        self.pdf_file = open(self.pdf_file_path, 'rb')
        self.pages = self.pdf_reader.getNumPages()
        for page in range(self.pages):
            self.pdf_writer.addPage(self.pdf_reader.getPage(page))
            with open(file_path + str(page) + '.pdf', 'wb') as f:
                self.pdf_writer.write(f)

    def merge_pdfs_from_folder_and_save(self, folder_path, file_path):
        """
        Merges PDFs from a folder and saves the PDF
        :param folder_path: The folder path of the PDFs to merge
        :param file_path: The file path to save the PDF
        """
        for file in os.listdir(folder_path):
            if file.endswith('.pdf'):
                self.pdf_file_path = folder_path + file
                self.pdf_file = open(self.pdf_file_path, 'rb')
                self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file)
                self.pages = self.pdf_reader.getNumPages()
                for page in range(self.pages):
                    self.pdf_writer.addPage(self.pdf_reader.getPage(page))
        with open(file_path, 'wb') as f:
            self.pdf_writer.write(f)

    def merge_pdfs_from_list_and_save(self, pdf_list, file_path):
        """
        Merges PDFs from a list and saves the PDF
        :param pdf_list: The list of PDFs to merge
        :param file_path: The file path to save the PDF
        """
        for pdf in pdf_list:
            self.pdf_file_path = pdf
            self.pdf_file = open(self.pdf_file_path, 'rb')
            self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file)
            self.pages = self.pdf_reader.getNumPages()
            for page in range(self.pages):
                self.pdf_writer.addPage(self.pdf_reader.getPage(page))
        with open(file_path, 'wb') as f:
            self.pdf_writer.write(f)

    def get_document_metadata(self):
        """
        Returns the document metadata
        :return: The document metadata
        """
        return self.pdf_reader.getDocumentInfo()

    def watermark(input_pdf, output_pdf, watermark_pdf):
        """
        Adds a watermark to a PDF
        :param output_pdf: The file path to save the PDF
        :param watermark_pdf: The file path of the watermark PDF
        """
        watermark = PdfFileReader(watermark_pdf)
        watermark_page = watermark.getPage(0)

        pdf = PdfFileReader(input_pdf)
        pdf_writer = PdfFileWriter()

        for page in range(pdf.getNumPages()):
            pdf_page = pdf.getPage(page)
            pdf_page.mergePage(watermark_page)
            pdf_writer.addPage(pdf_page)

        with open(output_pdf, 'wb') as fh:
            pdf_writer.write(fh)

    def encrypt(input_pdf, output_pdf, password):
        """
        Encrypts a PDF
        :param output_pdf: The file path to save the PDF
        :param password: The password to encrypt the PDF with
        """
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(input_pdf)

        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

        pdf_writer.encrypt(user_pwd=password, owner_pwd=None,
                           use_128bit=True)
        with open(output_pdf, 'wb') as fh:
            pdf_writer.write(fh)

    def decrypt(input_pdf, output_pdf, password):
        """
        Decrypts a PDF
        :param output_pdf: The file path to save the PDF
        :param password: The password to decrypt the PDF with
        """
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(input_pdf)

        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

        pdf_writer.decrypt(password)
        with open(output_pdf, 'wb') as fh:
            pdf_writer.write(fh)

    def rotate_page_clockwise(self, page_number):
        """
        Rotates a page clockwise
        :param page_number: The page number to rotate
        """
        self.pdf_reader.getPage(page_number).rotateClockwise(90)

    def rotate_page_counterclockwise(self, page_number):
        """
        Rotates a page counterclockwise
        :param page_number: The page number to rotate
        """
        self.pdf_reader.getPage(page_number).rotateCounterClockwise(90)

    def rotate_page_180(self, page_number):
        """
        Rotates a page 180 degrees
        :param page_number: The page number to rotate
        """
        self.pdf_reader.getPage(page_number).rotateClockwise(180)

    def rotate_page_90(self, page_number):
        """
        Rotates a page 90 degrees
        :param page_number: The page number to rotate
        """
        self.pdf_reader.getPage(page_number).rotateClockwise(90)

    def fill_form(self, file_path, data):
        """
        Fills a PDF form
        :param file_path: The file path to save the PDF
        :param data: The data to fill the form with as a json string
        """
        # convert json into dict
        data = json.loads(data)
        self.pdf_file_path = file_path
        self.pdf_file = open(self.pdf_file_path, 'rb')
        self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file)
        self.pdf_writer = PyPDF2.PdfFileWriter()
        self.pages = self.pdf_reader.getNumPages()
        for page in range(self.pages):
            self.pdf_writer.addPage(self.pdf_reader.getPage(page))
        self.pdf_writer.updatePageFormFieldValues(data)
        with open(file_path, 'wb') as f:
            self.pdf_writer.write(f)

    def get_form_fields(self):
        """
        Returns the form fields
        :return: The form fields
        """
        return self.pdf_reader.getFields()

    def get_form_textfield_values(self):
        """
        Returns the form field values
        :return: The form field values
        """
        return self.pdf_reader.getFormTextFields()

    def get_form_textfield_names(self):
        """
        Returns the form field names
        :return: The form field names
        """
        return self.pdf_reader.getFormTextFields().keys()

    def get_form_textfield_items(self):
        """
        Returns the form field items
        :return: The form field items
        """
        return self.pdf_reader.getFormTextFields().items()

    def get_form_textfield_value(self, field_name):
        """
        Returns a form field value
        :param field_name: The name of the form field
        :return: The form field value
        """
        return self.pdf_reader.getFormTextFields()[field_name]

    def print_pdf(self, file_path=""):
        """
        Prints the PDF
        :param file_path: Optional. The file path of the PDF to print. Leaving this blank will print the PDF that was opened with the class.
        """
        if file_path:
            self.pdf_file_path = file_path
        self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file_path)
        self.pages = self.pdf_reader.getNumPages()
        for page in range(self.pages):
            self.pdf_writer.addPage(self.pdf_reader.getPage(page))
        with open(self.pdf_file_path, 'wb') as f:
            self.pdf_writer.write(f)
        os.startfile(self.pdf_file_path, "print")













