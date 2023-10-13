# PieMenu2 piemgr.py for FreeCAD
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

import time

import FreeCAD as App
import FreeCADGui as Gui
from PySide2.QtWidgets import QApplication,QDockWidget
from PySide2.QtCore import QObject, QRect, QEvent, Signal, Qt
from PySide2.QtGui import QCursor, QKeySequence
from threading import Timer
from piemenuui import PieMenuUI
from pmtree import PMTreeNode,delNumber




class PMManager(QObject):
    __wb_list = {}

    __global_wb = None
    __current_wb = None
    __cur_menu = None
    __mainwindow = None

    __wbloaded = Signal()
    def __init__(self):
        super().__init__()
        self.evtobj = None
        self.__wb_list = {}
        self.__global_wb = None
        self.__current_wb = []
        self.enable = False
        self.presskey = 0
        self.releasekey = 0
        self.__mainwindow = Gui.getMainWindow()
        self.__mainwindow.workbenchActivated.connect(self.onWorkbenchActivated)
        self.__wbloaded.connect(self.onWorkbenchActivated)

        self.reloadConfig()
        if self.iskeydebug:
            print("PMManager init complete!")

    def reloadConfig(self):
        path = "User parameter:BaseApp/PieMenu2/Setting"
        param = App.ParamGet(path)
        self.radius = param.GetInt("Radius")
        if self.radius == 0:
            param.SetInt("Radius",100)
            self.radius = 100

        self.matchmode = param.GetInt("MatchMode")

        self.globalstyle = param.GetBool("GlobalStyle")
        self.cmd_style = param.GetString("CommandStyle")
        self.label_style = param.GetString("LabelStyle")

        self.iskeydebug = param.GetBool("KeymapDebug")

        self.maxWidth = param.GetInt("maxWidth")
        if self.maxWidth == 0:
            param.SetInt("maxWidth",130)
            self.maxWidth = 130

        if self.enable:
            self.unregisterEventFilter()
            self.enable = False

        if param.GetBool("Enable"):
            self.enable = True
            self.registerEventFilter()

    def eventFilter(self, watched, event):
        if self.evtobj != watched:
            if watched.objectName() == "Gui::MainWindowClassWindow":
                self.evtobj = watched
        else:
            if event.type() == QEvent.KeyPress and not event.isAutoRepeat():
                if self.presskey != event.key():
                    res = self.onKeyPress(QKeySequence(event.modifiers() | event.key()).toString())
                    self.presskey = event.key()
                    self.releasekey = 0
                    return res
                # return self.onKeyPress(QKeySequence(event.modifiers() | event.key()))

            if event.type() == QEvent.KeyRelease and not event.isAutoRepeat():
                if self.releasekey != event.key():
                    res = self.onKeyRelease(QKeySequence(event.modifiers() | event.key()).toString())
                    self.releasekey = event.key()
                    self.presskey = 0
                    return res
            # return self.onKeyRelease(QKeySequence(event.modifiers() | event.key()))
        return super(PMManager, self).eventFilter(watched, event)

    def onKeyPress(self, keymap):
        if self.iskeydebug:
            print("PressKey", keymap)

        pt = QCursor.pos()
        if self.canShowMenu(pt):
            if self.__cur_menu and not self.__cur_menu.isHidden():
                return True
            self.__cur_menu = self.matchMenu(keymap)
            if self.__cur_menu and self.__cur_menu.trigger == "Press":
                self.__cur_menu.showMenu(pt.x(), pt.y())
                return True
        return False

    def onKeyRelease(self, keymap):
        if self.iskeydebug:
            print("ReleaseKey", keymap)
        if self.__cur_menu == None:
            return False

        if self.__cur_menu.trigger == "Press":
            if not self.__cur_menu.isHidden():
                self.__cur_menu.hideMenu(True)
                return True
        else:
            if self.__cur_menu.isHidden():
                pt = QCursor.pos()
                self.__cur_menu.showMenu(pt.x(), pt.y())
                return True
            else:
                if self.__cur_menu.keymap == keymap:
                    self.__cur_menu.hideMenu(True)
                    return True
        return False

    def canShowMenu(self, pos):
        cent = self.__mainwindow.centralWidget()
        pt = self.__mainwindow.mapToGlobal(cent.pos())
        return QRect(pt, cent.size()).contains(pos)

    def matchMenuTree(self,node,sel,num,stk):
        count = len(sel)
        if count == 1:
            if num == 0:
                obj = delNumber(sel[0].ObjectName)
                n = node.getNode(obj)
                if n == None:
                    n = node.getNode('*')
                if n != None:
                    stk.append(n)
                    if n.count() != 0:
                        num += 1
                        if (len(sel[0].SubElementNames)) != 0:
                            n1 = self.matchMenuTree(n,sel,num,stk)
                            if n1 != None:
                                return n1
                        else:
                            return n
                        num -= 1
                    else:
                        if(len(sel[0].SubElementNames)) == 0:
                            return n
            else:
                if num == 1:
                    n = node.getNode(delNumber(sel[0].SubElementNames[0]))
                    if n != None:
                        stk.append(n)
                        return n
        elif count > 1:
            if num == 0:
                ret = node.getMultiSelectionObject(sel)
                if ret == None:
                    for n in node.children:
                        if n.object == '':
                            continue
                        if n.object == '*+':
                            ret = n
                if ret:
                    stk.append(ret)
                    return ret
        else:
            if num == 0:
                return node
        return None

    def matchMenu(self, keymap):
        doc = App.ActiveDocument
        if doc == None:
            return
        sel = Gui.Selection.getSelectionEx(doc.Name)
        view = str(Gui.activeView())

        menu_stack = [None]

        if keymap in self.__global_wb:
            root = self.__global_wb[keymap]
            if len(root.children) == 0 and root.disable == False and root.view == view:
                return root.menu
            laver = 0
            node = self.matchMenuTree(root,sel,laver,menu_stack)
            if node != None and node.disable == False and node.view == view:
                return node.menu

        if keymap in self.__current_wb:
            root = self.__current_wb[keymap]
            menu_stack.append(root)
            laver = 0
            node = self.matchMenuTree(root,sel,laver,menu_stack)
            ret_node = None
            if self.matchmode == 0:
                ret_node = node
            elif self.matchmode == 1:
                if not node:
                    ret_node = root
                else:
                    ret_node = node
            else:
                if self.matchmode == 2:
                    ret_node = menu_stack.pop()
            if ret_node and ret_node.disable == False and ret_node.view == view:
                return ret_node.menu
        return None

    def onMenuHide(self):
        self.__cur_menu = None

    def registerEventFilter(self):
        #self.__mainwindow.installEventFilter(self)
        QApplication.instance().installEventFilter(self)
        pass

    def unregisterEventFilter(self):
        #self.__mainwindow.removeEventFilter(self)
        QApplication.instance().removeEventFilter(self)
        pass



    def loadPieMenu(self, wb):
        path = "User parameter:BaseApp/PieMenu2/Menus/" + wb + "/"
        param = App.ParamGet(path)
        menus = {}
        for m in param.GetGroups():
            pm = App.ParamGet(path + m + '/')
            key = pm.GetString('TriggerKey')
            if key != "":
                node = self.loadPieMenuTree(path+m+'/',key)
                menus[key] = node
        return menus

    def loadPieMenuTree(self,path,keymap):

        pm = App.ParamGet(path)
        pmnode = PMTreeNode()
        pmnode.disable = not pm.GetBool('Enable')
        rule = pm.GetString('TriggerRule')
        res = rule.split(":")
        tview = "View3DInventor"
        s = rule
        if len(res) == 2:
            tview = res[0]
            s = res[1]

        pmnode.view = tview
        pmnode.object = s
        menu = PieMenuUI(Gui.getMainWindow(), pm.GetGroupName(), self.radius)
        menu.loadPieMenu(path,self.maxWidth)
        if not self.globalstyle:
            menu.setStyleSheet(self.label_style)
            menu.setCommandButtonStylesheet(self.cmd_style)
        menu.onMenuHide.connect(self.onMenuHide)
        menu.keymap = keymap
        pmnode.menu = menu

        for item in pm.GetGroups():
            res = self.loadPieMenuTree(path+item+'/',keymap)
            pmnode.addChild(res)
        return pmnode

    def onWaitWorkbenchLoaded(self):
        while True:
            wb = Gui.activeWorkbench()
            if not hasattr(wb, "__Workbench__"):
                time.sleep(0.1)
                if self.timerCount > 30:
                    break
                self.timerCount += 1
            else:
                self.__wbloaded.emit()
                break
    def reloadWorkbench(self):
        self.__wb_list.clear()
        self.__global_wb = None
        self.__current_wb = None
        self.__cur_menu = None
        self.onWorkbenchActivated()

    def onWorkbenchActivated(self):
        wb = Gui.activeWorkbench()

        if self.__global_wb == None:
            self.__global_wb = self.loadPieMenu("Global")

        if hasattr(wb, "__Workbench__"):
            wbname = wb.name()
            if not wbname in self.__wb_list.keys():
                self.__wb_list[wbname] = self.loadPieMenu(wbname)
            self.__current_wb = self.__wb_list.get(wbname)
            if self.iskeydebug:
                print("current workbench piemenu changed '" + wbname + "'")
        else:
            self.timerCount = 0
            self.timerwb = Timer(0.1,self.onWaitWorkbenchLoaded)
            self.timerwb.start()
