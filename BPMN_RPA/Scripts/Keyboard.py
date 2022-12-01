import pyautogui
import keyboard


# The BPMN-RPA Keyboard module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Keyboard module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA Images module is based on the PyAutoGUI library, which is licensed under the BSD 3-Clause "New" or "Revised" License:
# Copyright (c) 2014, Al Sweigart
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the PyAutoGUI nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The BPMN-RPA Keyboard module is also based on the Keyboard library, which is licensed under the MIT License:
# Copyright (c) 2016 BoppreH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



def sendkeys(text: str, interval: float = 0.05):
    """
    Send keys to the foreground window.
    :param text: the text to send to the foreground window.
    :param interval: The text to send to the foreground window.
    """
    pyautogui.write(text, interval=interval)


def press_key(key: str, presses: int = 3, interval: float = 0.05):
    """
    Press a specific key on the keyboard.
    :param key: The key to press.
    :param presses: The number of times the key should be pressed.
    :param interval: The interval between keypresses.
    """
    pyautogui.press(key, presses=presses, interval=interval)


def wait_for_hotkey(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    """
    Wait for a specific hotkey to be pressed.
    :param key: The key on the keyboard.
    :param ctrl: Optional. Boolean: indicator whether the control button should be pressed.
    :param alt: Optional. Boolean: indicator whether the alt button should be pressed.
    :param shift: Optional. Boolean: indicator whether the shift button should be pressed.
    """
    hotkey = key
    if ctrl:
        hotkey += "+ctrl"
    if alt:
        hotkey += "+alt"
    if shift:
        hotkey += "+shift"
    while True:
        if keyboard.is_pressed(hotkey):
            return True


def wait_for_key_release(key: str):
    """
    Wait for a specific key to be released.
    :param key: The key on the keyboard.
    """
    while True:
        if keyboard.is_pressed(key):
            return False


def wait_for_key_press(key: str):
    """
    Wait for a specific key to be pressed.
    :param key: The key on the keyboard.
    """
    while True:
        if keyboard.is_pressed(key):
            return True


def wait_for_key_combination_release(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    """
    Wait for a specific key combination to be released.
    :param key: The key on the keyboard.
    :param ctrl: Optional. Boolean: indicator whether the control button should be pressed.
    :param alt: Optional. Boolean: indicator whether the alt button should be pressed.
    :param shift: Optional. Boolean: indicator whether the shift button should be pressed.
    """
    while True:
        if keyboard.is_pressed(key):
            if ctrl:
                if keyboard.is_pressed("ctrl"):
                    return False
            if alt:
                if keyboard.is_pressed("alt"):
                    return False
            if shift:
                if keyboard.is_pressed("shift"):
                    return False


def wait_for_key_combination_press(key: str, ctrl: bool = False, alt: bool = False, shift: bool = False):
    """
    Wait for a specific key combination to be pressed.
    :param key: The key on the keyboard.
    :param ctrl: Optional. Boolean: indicator whether the control button should be pressed.
    :param alt: Optional. Boolean: indicator whether the alt button should be pressed.
    :param shift: Optional. Boolean: indicator whether the shift button should be pressed.
    """
    while True:
        if keyboard.is_pressed(key):
            if ctrl:
                if keyboard.is_pressed("ctrl"):
                    return True
            if alt:
                if keyboard.is_pressed("alt"):
                    return True
            if shift:
                if keyboard.is_pressed("shift"):
                    return True
