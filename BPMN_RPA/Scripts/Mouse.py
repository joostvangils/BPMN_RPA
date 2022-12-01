import pyautogui


# The BPMN-RPA Mouse module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Mouse module is distributed in the hope that it will be useful,
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

def get_mouse_position():
    """
    Retrieve the coordinates of the mouse position.
    :return: Point object with X and Y values.
    """
    return pyautogui.position()


def mouse_move(x: int, y: int, duration: int = 0):
    """
    Move the mouse to a specific coordinate on the screen.
    :param x: The horizontal position on the screen to move to.
    :param y: The vertical position on the screen to move to.
    :param duration: Optional. The time to take for the mouse move.
    """
    pyautogui.moveTo(x, y, duration)


def mouse_drag(x: int, y: int):
    """
    Drag the mouse to a specific coordinate on the screen.
    :param x: The horizontal position on the screen.
    :param y: The vertical position on the screen.
    """
    pyautogui.dragTo(x, y)


def mouse_click(button: str = 'right', clicks: int = 1, interval: float = 0.25):
    """
    Simulate a click on a mouse button.
    :param button: Optional. The button to click (left, right).
    :param clicks: Optional. The number of times the button should be clicked.
    :param interval: Optional. The interval between clicks.
    """
    pyautogui.click(button=button, clicks=clicks, interval=interval)


def mouse_doubleclick():
    """
    Simulate a double-click on the left mouse button.
    """
    pyautogui.doubleClick()


def mouse_button_down(button: str = 'right'):
    """
    Simulate mouse button down.
    :param button: Optional. The button to press (left, right).
    """
    pyautogui.mouseDown(button=button)


def mouse_button_up(button: str = 'right'):
    """
    Simulate mouse button up.
    :param button: Optional. The button to relesase (left, right).
    """
    pyautogui.mouseUp(button=button)


def mouse_scroll_up(clicks: int):
    """
    Simulate mouse scroll up.
    :param clicks: number of clicks to scroll up.
    """
    pyautogui.scroll(clicks)


def mouse_scroll_down(clicks: int):
    """
    Simulate mouse scroll down.
    :param clicks: number of clicks to scroll down.
    """
    pyautogui.scroll(-clicks)


def mouse_scroll_left(clicks: int):
    """
    Simulate mouse scroll left.
    :param clicks: number of clicks to scroll left.
    """
    pyautogui.hscroll(-clicks)


def mouse_scroll_right(clicks: int):
    """
    Simulate mouse scroll right.
    :param clicks: number of clicks to scroll right.
    """
    pyautogui.hscroll(clicks)

def block_mouse_input():
    """
    Block mouse input.
    """
    pyautogui.FAILSAFE = False

def unblock_mouse_input():
    """
    Unblock mouse input.
    """
    pyautogui.FAILSAFE = True

