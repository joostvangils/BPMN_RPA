import pyautogui
from PIL import Image


# The BPMN-RPA Images module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Images module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def click_on_image(image: str, confidence: float = 0.9):
    """
    Click on an image on the screen.
    :param image: The image to click on.
    :param confidence: Optional. The confidence level for the image match.
    :return: True if the image was found and clicked, False otherwise.
    """
    pos = pyautogui.locateOnScreen(image, confidence=confidence)
    if pos is not None:
        pyautogui.click(pos)
        return True
    else:
        print("image not found")
        return False


def ocr_text_from_image(image: str, path_to_tesseract: str = None, lang: str = 'eng'):
    """
    Get the text from an image.
    :param image: The full path to the image
    :param path_to_tesseract: Optional. The full path to the Tesseract executable.
    :param lang: Optional. The language to use for the OCR.
    :return:
    """
    from pytesseract import pytesseract
    if path_to_tesseract is not None:
        pytesseract.tesseract_cmd = path_to_tesseract
    return pytesseract.image_to_string(Image.open(image), lang=lang)

