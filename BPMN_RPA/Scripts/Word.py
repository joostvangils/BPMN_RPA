import pickle

import win32com
import win32com.client

# The BPMN-RPA Word module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Word module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


class Word:

    def __init__(self, path):
        """
        Opens a Word document and initializes the class for later use
        :param path: Path to the Word document
        """
        self.path = path
        self.word = win32com.client.Dispatch("Word.Application")
        self.word.Visible = 0
        self.doc = self.word.Documents.Open(self.path)
        self.doc.Activate()

    def __connect__(self):
        """
        Internal function to connect to the Word document
        """
        self.word = win32com.client.Dispatch("Word.Application")
        self.word.Visible = 0
        self.doc = self.word.Documents.Open(self.path)
        self.doc.Activate()

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
        self.word_close(save_changes=True)
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

    def word_replace(self, old, new):
        """
        Replaces text in the Word document
        :param old: Text to replace
        :param new: Text to replace with
        """
        self.word.Selection.Find.ClearFormatting()
        self.word.Selection.Find.Replacement.ClearFormatting()
        self.word.Selection.Find.Execute(old, False, False, False, False, False, True, 1, True, new, 2)

    def word_close(self, save_changes=True):
        """
        Closes the Word document
        :param save_changes: Save changes to the Word document
        """
        self.doc.Close(SaveChanges=save_changes)
        self.word.Quit()

    def word_save(self):
        """
        Saves the Word document
        """
        self.doc.Save()

    def word_save_as(self, path):
        """
        Saves the Word document as a new file
        :param path: Path to save the Word document
        """
        self.doc.SaveAs(path)

    def word_save_as_pdf(self, path):
        """
        Saves the Word document as a PDF
        :param path: Path to save the PDF
        """
        self.doc.SaveAs(path, FileFormat=17)

    def word_close(self):
        """
        Closes the Word document
        """
        self.doc.Close()
        self.word.Quit()

    def word_close_without_saving(self):
        """
        Closes the Word document without saving
        """
        self.doc.Close(SaveChanges=0)
        self.word.Quit()

    def word_insert_text_at_beginning(self, text):
        """
        Inserts text at the beginning of the Word document
        :param text: Text to insert
        """
        self.word.Selection.HomeKey(Unit=6)
        self.word.Selection.TypeText(text)

    def word_insert_text_at_end(self, text):
        """
        Inserts text at the end of the Word document
        :param text: Text to insert
        """
        self.word.Selection.EndKey(Unit=6)
        self.word.Selection.TypeText(text)

    def word_insert_text_at_cursor(self, text):
        """
        Inserts text at the cursor position in the Word document
        :param text: Text to insert
        """
        self.word.Selection.TypeText(text)

    def word_insert_text_at_bookmark(self, bookmark, text):
        """
        Inserts text at a bookmark in the Word document
        :param bookmark: Bookmark to insert text at
        :param text: Text to insert
        """
        self.word.Selection.GoTo(What=1, Name=bookmark)
        self.word.Selection.TypeText(text)

    def word_insert_table_from_list_string(self, list_string):
        """
        Inserts a table from a list of strings
        :param list_string: List of strings to insert
        """
        self.word.Selection.TypeText(list_string)

