# PieMenu2 InitGui for FreeCAD
#
# Copyright (C) 2023 sxgsgnh <sxgsgnh@sina.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

# Attribution:
# http://forum.freecadweb.org/
# http://www.freecadweb.org/wiki/index.php?title=Code_snippets

import FreeCADGui as Gui


def piemenu_run(name):
    if name != "NoneWorkbench":
        mw = Gui.getMainWindow()
        mw.workbenchActivated.disconnect(piemenu_run)
        import piemenuuiloader
        piemenuuiloader.piemenurun()


import __main__
__main__.piemenu_run = piemenu_run

Gui.getMainWindow().workbenchActivated.connect(piemenu_run)
