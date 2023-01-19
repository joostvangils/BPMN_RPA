import matplotlib.pyplot as plt


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
# BPMN-RPA makes also use of the Mathplotlib module, copyright John D. Hunter andf Michael Droettboom, 
# which is licensed under the Python Software Foundation License (PSF):
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
# grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
# analyze, test, perform and/or display publicly, prepare derivative works,
# distribute, and otherwise use Python alone or in any derivative version,
# provided, however, that PSF's License Agreement and PSF's notice of copyright,
# i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012 Python Software Foundation; All Rights Reserved" are retained in
# Python alone or in any derivative version prepared by Licensee.
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.


class RiskMatrix:

    def __init__(self, title="Risk Matrix", x_label='probability', y_label='Impact', draw_limit=True,
                 limit_label='Risk tolerance limit'):
        self.plt = plt
        self.fig = self.plt.figure()
        self.plt.subplots_adjust(wspace=0, hspace=0)
        self.plt.xticks([])
        self.plt.yticks([])
        self.plt.xlim(0, 5)
        self.plt.ylim(0, 5)
        self.plt.xlabel(x_label)
        self.plt.ylabel(y_label)
        self.plt.title(title)
        # This example is for a 5 * 5 matrix
        nrows = 5
        ncols = 5
        self.axes = [self.fig.add_subplot(nrows, ncols, r * ncols + c + 1) for r in range(0, nrows) for c in
                     range(0, ncols)]
        # remove the x and y ticks
        for ax in self.axes:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(0, 5)
            ax.set_ylim(0, 5)
        self.green = [10, 15, 16, 20, 21]  # Green boxes
        self.yellow = [0, 5, 6, 11, 17, 22, 23]  # yellow boxes
        self.orange = [1, 2, 7, 12, 13, 18, 19, 24]  # orange boxes
        self.red = [3, 4, 8, 9, 14]  # red boxes
        for _ in self.green:
            self.axes[_].set_facecolor('green')
        for _ in self.yellow:
            self.axes[_].set_facecolor('yellow')
        for _ in self.orange:
            self.axes[_].set_facecolor('orange')
        for _ in self.red:
            self.axes[_].set_facecolor('red')
        if draw_limit:
            self.axes[0].axhline(y=4.95, xmin=0, xmax=1, color="blue", linestyle="-")
            self.axes[0].axvline(x=4.95, ymin=0, ymax=1, color="blue", linestyle="-")
            self.axes[1].axhline(y=0.05, xmin=0, xmax=1, color="blue", linestyle="-")
            self.axes[6].axvline(x=4.94, ymin=0, ymax=1, color="blue", linestyle="-")
            self.axes[17].axhline(y=4.95, xmin=0, xmax=1, color="blue", linestyle="-")
            self.axes[11].axvline(x=4.94, ymin=0, ymax=1, color="blue", linestyle="-")
            self.axes[18].axhline(y=4.95, xmin=0, xmax=1, color="blue", linestyle="-")
            self.axes[18].axvline(x=4.95, ymin=0, ymax=1, color="blue", linestyle="-")
            self.axes[24].axhline(y=4.95, xmin=0, xmax=1, color="blue", linestyle="-", label=limit_label)
            self.fig.legend(loc="lower center", fontsize=5)

    def plot(self, text, probability=3, impact=3, fontsize=7):
        color = 'black'
        cell = 12
        if impact == 1 and probability == 1:
            cell = 20
            color = 'white'
        if impact == 1 and probability == 2:
            cell = 21
            color = 'white'
        if impact == 1 and probability == 3:
            cell = 22
        if impact == 1 and probability == 4:
            cell = 23
        if impact == 1 and probability == 5:
            cell = 24
        if impact == 2 and probability == 1:
            cell = 15
            color = 'white'
        if impact == 2 and probability == 2:
            cell = 16
            color = 'white'
        if impact == 2 and probability == 3:
            cell = 17
        if impact == 2 and probability == 4:
            cell = 18
        if impact == 2 and probability == 5:
            cell = 19
        if impact == 3 and probability == 1:
            cell = 10
            color = 'white'
        if impact == 3 and probability == 2:
            cell = 11
        if impact == 3 and probability == 3:
            cell = 12
        if impact == 3 and probability == 4:
            cell = 13
        if impact == 3 and probability == 5:
            cell = 14
            color = 'white'
        if impact == 4 and probability == 1:
            cell = 5
        if impact == 4 and probability == 2:
            cell = 6
        if impact == 4 and probability == 3:
            cell = 7
        if impact == 4 and probability == 4:
            cell = 8
            color = 'white'
        if impact == 4 and probability == 5:
            cell = 9
            color = 'white'
        if impact == 5 and probability == 1:
            cell = 0
        if impact == 5 and probability == 2:
            cell = 1
        if impact == 5 and probability == 3:
            cell = 2
        if impact == 5 and probability == 4:
            cell = 3
            color = 'white'
        if impact == 5 and probability == 5:
            cell = 4
            color = 'white'
        if len(self.axes[cell].text) > 0:
            txt = self.axes[cell].text + ", " + text
        else:
            txt = text
        self.axes[cell].text(x=1, y=2.5, s=txt, ha='center', va='center', c=color, size=fontsize)

    def show(self, bitmap_icon_path=''):
        if len(bitmap_icon_path) > 0:
            thismanager = self.plt.get_current_fig_manager()
            thismanager.window.wm_iconbitmap(bitmap_icon_path)
        self.plt.show()

    def save_as_png(self, full_path: str):
        if not full_path.lower().endswith('.png'):
            full_path += '.png'
        self.plt.savefig(full_path)
