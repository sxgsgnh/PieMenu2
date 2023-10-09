# PieMenu2 piemenuuiloader.py for FreeCAD
#
# Copyright (C) 2017, 2018, 2019 (as part of ui loader) triplus @ FreeCAD
# Copyright (C) 2023 sxgsgnh <sxgsgnh@sina.com>

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

from PySide2.QtWidgets import QAction,QMenu
from PySide2.QtCore import QTimer
import FreeCAD as App
import FreeCADGui as Gui
from piemgr import PMManager
import piemenusetting

mw = Gui.getMainWindow()

piemenu_manager = PMManager()

t = None

def onWorkbench():
    """Temp"""
    pass


def accessoriesMenu():
    """Add pie menu preferences to accessories menu."""
    pref = QAction(mw)
    pref.setText("PieMenu2")
    pref.setObjectName("PieMenu2")
    pref.triggered.connect(onPreferences)
    try:
        import AccessoriesMenu
        AccessoriesMenu.addItem("PieMenu2")
    except ImportError:
        a = mw.findChild(QAction, "AccessoriesMenu")
        if a:
            a.menu().addAction(pref)
        else:
            mb = mw.menuBar()
            action = QAction(mw)
            action.setObjectName("AccessoriesMenu")
            action.setIconText("Accessories")
            menu = QMenu()
            action.setMenu(menu)
            menu.addAction(pref)

            def addMenu():
                """Add accessories menu to the menu bar."""
                mb.addAction(action)
                action.setVisible(True)

            addMenu()
            mw.workbenchActivated.connect(addMenu)


window = None

def onPreferences():
    piemenusetting.showPMenuEditor(piemenu_manager)
    pass


def onStart():
    """Start pie menu."""
    start = False
    try:
        mw.mainWindowClosed
        mw.workbenchActivated
        start = True
    except AttributeError:
        pass
    if start:
        t.stop()
        t.deleteLater()
        onWorkbench()
        accessoriesMenu()
        mw.mainWindowClosed.connect(onClose)
        mw.workbenchActivated.connect(onWorkbench)
        # a = QtGui.QAction(mw)
        # mw.addAction(a)
        # a.setText("Invoke pie menu")
        # a.setObjectName("InvokePieMenu")
        # a.setShortcut(QtGui.QKeySequence("Q"))
        # a.triggered.connect(onInvoke)


def onClose():
    """Remove system presets and groups without index on FreeCAD close."""
    pass



def onPreStart():
    """Improve start reliability and maintain FreeCAD 0.16 support."""
    if App.Version()[1] < "17":
        onStart()
    else:
        if mw.property("eventLoop"):
            onStart()


def piemenurun():
    global t
    t = QTimer()
    t.timeout.connect(onPreStart)
    t.start(500)