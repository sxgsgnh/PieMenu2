# PieMenu2 piemenuui.py for FreeCAD
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

from PySide2.QtWidgets import QPushButton, QWidget
from PySide2.QtWidgets import QStylePainter, QStyleOptionButton, QStyle
from PySide2.QtCore import Qt,QPoint,QRect,Signal
from PySide2.QtGui import QRegion, QPainter
import math
import FreeCAD as App
import FreeCADGui as Gui

class PiePushButton(QPushButton):
    bHover = None
    bPress = None
    command = ""
    command_index = 0

    x_offset = 0
    y_offset = 0
    isActive = True
    def __init__(self, parent):
        super().__init__(parent)
        self.__isActive = True
        self.setWindowFlags(Qt.ToolTip | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_Hover)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(100)
        self.setMaximumWidth(130)
        self.bPress = False
        self.bHover = False
        self.y_offset = self.x_offset = 0
        self.hide()

    def setCommand(self,cmd,index):
        c = Gui.Command.get(cmd)
        act = c.getAction()[index]

        self.setIcon(act.icon())
        fm = self.fontMetrics()
        fontsize = fm.width(act.text())
        if fontsize > self.maximumWidth()-self.iconSize().width():
            self.setText(fm.elidedText(act.text(),Qt.ElideRight,self.maximumWidth()-self.iconSize().width()))
        else:
            self.setText(act.text())

        self.command = cmd
        self.command_index = index

    def checkCmdActive(self):
        self.isActive = Gui.Command.get(self.command).isActive()
        return self.isActive

    def paintEvent(self, arg__1):
        paint = QStylePainter(self)
        option = QStyleOptionButton()
        option.initFrom(self)

        if self.bHover:
            option.state |= QStyle.State_MouseOver
        else:
            if self.bPress:
                option.state |= QStyle.State_Sunken
            else:
                option.state |= QStyle.State_Raised
        option.text = self.text()
        option.icon = self.icon()
        option.iconSize = self.iconSize()
        paint.drawControl(QStyle.CE_PushButton, option)
        pass


    def Hover(self, hover):
        self.bHover = hover
        self.update()
        pass

    def Press(self):
        self.bPress = True
        self.bHover = False
        self.update()

    def Release(self,bhover = True):
        self.bPress = False
        self.bHover = bhover
        self.update()


class PieMenuUI(QWidget):
    name = "Default"
    keymap = ""
    trigger = ""
    radius = 100
    __origin = None
    __selected = None
    __prevselected = None
    __lstPieButton = None

    pieCenterSpan = 60

    onMenuHide = Signal()

    def __init__(self, parent, name,radius=130):
        super().__init__(parent)
        self.keymap = ''
        self.angle = 0
        self.setWindowFlags(Qt.ToolTip | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(40, 40)
        inner = 9
        reg = QRegion(self.rect().adjusted(inner,inner,-inner,-inner),QRegion.Ellipse)
        reg1 = QRegion(self.rect(),QRegion.Ellipse)
        self.setMask(reg1.subtracted(reg))

        self.name = name
        self.radius = radius
        self.setMouseTracking(True)
        self.__lstPieButton = [None] * 8

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.fillRect(self.rect(),self.palette().background())
        p.setBrush(self.palette().foreground())
        p.drawPie(self.rect(),-(self.angle+self.pieCenterSpan/2)*16,self.pieCenterSpan*16)
        pass

    def loadPieMenu(self,menupath,width):
        param = App.ParamGet(menupath)
        self.trigger = param.GetString("TriggerMode")
        self.keymap = param.GetString("TriggerKey")
        for id in range(8):
            cmd = param.GetString('Command_'+str(id))
            if cmd != "":
                command = cmd.split('-')
                self.setMaximumWidth(width)
                self.setCommand(id, command[0], int(command[1]))

    def setCommand(self,pos, cmd,index):
        bcmd = PiePushButton(self)
        bcmd.setCommand(cmd,index)
        value = (pos * 45) * math.pi / 180
        bcmd.x_offset = self.radius * math.cos(value)
        bcmd.y_offset = self.radius * math.sin(value)
        bcmd.show()
        sz = bcmd.size()
        if pos == 0 :
            bcmd.y_offset = bcmd.y_offset - sz.height() / 2
        elif pos == 4:
            bcmd.y_offset = bcmd.y_offset - sz.height() / 2
            bcmd.x_offset = bcmd.x_offset - sz.width()
        elif pos == 2:
            bcmd.x_offset = bcmd.x_offset - sz.width() / 2
        elif pos == 6:
            bcmd.x_offset = bcmd.x_offset - sz.width() / 2
            bcmd.y_offset = bcmd.y_offset - sz.height()
        elif pos == 1:
            bcmd.y_offset = bcmd.y_offset - sz.height()/2
            pass
        elif pos == 3 or pos == 5:
            bcmd.x_offset = bcmd.x_offset - sz.width()
            bcmd.y_offset = bcmd.y_offset - sz.height()/2
        elif pos == 7:
            bcmd.y_offset = bcmd.y_offset - sz.height()/2
        bcmd.hide()
        self.__lstPieButton[pos] = bcmd

    def removeCommand(self,pos):
        self.__lstPieButton[pos] = None

    def mouseMoveEvent(self, event):
        pt = self.mapToGlobal(event.pos())
        width = abs(pt.x() - self.__origin.x())
        height = abs(pt.y() - self.__origin.y())
        if width == 0:
            width = 0.01
        arc = math.atan(height / width)
        angle = arc*180/math.pi
        if pt.x() <= self.__origin.x() and pt.y() >= self.__origin.y():
            self.angle = 90+(90-angle)
        elif pt.x() <= self.__origin.x() and pt.y() <= self.__origin.y():
            self.angle = 180 + angle
        elif pt.x() >= self.__origin.x() and pt.y() <= self.__origin.y():
            self.angle = 270 + (90-angle)
        else:
            self.angle = angle
        self.update()
        newRadius = math.sqrt(width * width + height * height)
        sina = math.sin(arc)
        cosa = math.cos(arc)
        hoverbtn = None
        for i in range(self.radius-20, int(newRadius)):
            nx = 0;ny = 0
            if pt.x() > self.__origin.x():
                nx = self.__origin.x() + i * cosa
            else:
                nx = self.__origin.x() + -(i * cosa)
            if pt.y() > self.__origin.y():
                ny = self.__origin.y() + i * sina
            else:
                ny = self.__origin.y() + -(i * sina)
            for obj in self.__lstPieButton:
                if obj != None and obj.isActive:
                    rt = QRect(obj.pos(), obj.size())
                    if rt.contains(nx,ny):
                        hoverbtn = obj
                        break
            if hoverbtn:
                break

        if hoverbtn:
            if hoverbtn != self.__selected:
                self.__selected = hoverbtn
                self.__selected.Hover(True)
        else:
            if self.__selected:
                self.__selected.Release()
                self.__selected.Hover(False)
            self.__selected = None
        #p = event.pos()
        #print("x="+str(p.x())+",y="+str(p.y()))


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.hideMenu()
        if event.button() == Qt.LeftButton:
            if self.__selected:
                self.hideMenu(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.__selected:
                self.__prevselected = self.__selected
                self.__selected.Press()

    def showMenu(self, x, y):
        size = self.size()
        self.__origin = QPoint(x, y)
        self.move(x - size.width() / 2, y - size.height() / 2)

        for obj in self.__lstPieButton:
            if obj != None:
                obj.move(self.__origin.x()+obj.x_offset,self.__origin.y()+obj.y_offset)
                if not obj.checkCmdActive():
                    obj.setWindowOpacity(0.2)
                obj.show()

        self.grabMouse()
        self.show()

    def hideMenu(self,bRunCmd = False):
        for obj in self.__lstPieButton:
            if obj != None:
                if not obj.isActive:
                    obj.setWindowOpacity(1)
                obj.hide()
        self.releaseMouse()
        self.hide()
        if self.__selected:
            self.__selected.Release(False)
            if bRunCmd :
                Gui.runCommand(self.__selected.command,self.__selected.command_index)
            self.__selected = None
        self.onMenuHide.emit()

    def setCommandButtonStylesheet(self,style):
        for item in self.__lstPieButton:
            if item != None:
                item.setStyleSheet(style)

    def printCmd(self):
        print(len(self.__lstPieButton))
        for obj in self.__lstPieButton:
            #print(self.__lstPieButton[i].command)
            pass

