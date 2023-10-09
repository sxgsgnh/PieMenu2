# PieMenu2 piemenusetting.py for FreeCAD
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

from PySide2.QtWidgets import QWidget, QPushButton, QComboBox, QDialog, QMessageBox, QCheckBox, QRadioButton
from PySide2.QtWidgets import QTabWidget,QTreeWidget,QTreeWidgetItem,QKeySequenceEdit, QTextEdit, QLabel
from PySide2.QtWidgets import QInputDialog,QLineEdit,QToolButton,QSlider
from PySide2.QtWidgets import QHBoxLayout,QVBoxLayout,QFormLayout
from PySide2.QtCore import Qt,QSize
from PySide2.QtGui import QIcon,QKeySequence
from PySide2.QtCore import QObject,Signal
import FreeCADGui as Gui
import FreeCAD as App
import os

icondir = os.path.dirname( __file__)+"/Resources/icons/"

icons = ["arrow-square-right.svg", "arrow-square-down-right.svg", "arrow-square-down.svg", \
         "arrow-square-down-left.svg", "arrow-square-left.svg", "arrow-square-up-left.svg", \
         "arrow-square-up.svg", "arrow-square-up-right.svg"]

ParamsRoot = "User parameter:BaseApp/PieMenu2/"

titleName = "PieMenu2 Editor"

mw = Gui.getMainWindow()
editor = None

cmdfilter = ["File","Edit","Clipboard","Macro","View","Structure","Help"]

class PMCommandSelector(QDialog):
    def __init__(self,parent,wb):
        super().__init__(parent)
        self.setWindowTitle("PieMenu2 CommandSelector")
        self.setModal(True)
        self.workbench = wb
        self.resize(300,600)
        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setColumnCount(1)

        param = App.ParamGet(ParamsRoot+"Setting")
        layout = QVBoxLayout()
        self.toggleAll = QCheckBox("Show all command")
        self.toggleAll.stateChanged.connect(self.onShowAllCommandChanged)
        self.toggleAll.setChecked(param.GetBool("ShowAllCmd"))
        self.treeWidget.itemDoubleClicked.connect(self.onSelectedCommand)

        self.onShowAllCommandChanged(None)

        layout.addWidget(self.toggleAll)
        layout.addWidget(self.treeWidget)
        self.setLayout(layout)

    def onShowAllCommandChanged(self,state):
        param = App.ParamGet(ParamsRoot + "Setting")
        b = self.toggleAll.isChecked()
        param.SetBool("ShowAllCmd",b)
        if b:
            self.showAllCommand()
        else:
            self.showToolbarCommand()
    def showToolbarCommand(self):
        self.treeWidget.clear()
        wob = Gui.activeWorkbench()
        if self.workbench != "Global":
            wob = Gui.getWorkbench(self.workbench)
        for k,v in wob.getToolbarItems().items():
            if self.workbench == "Global":
                if not k in cmdfilter:
                    continue
            items = QTreeWidgetItem()
            items.setText(0,k)
            for item in v:
                if item == "Separator":
                    continue
                cmd = Gui.Command.get(item)
                num = 0
                for act in cmd.getAction():
                    cmditem = QTreeWidgetItem()
                    cmditem.setText(0,act.text())
                    cmditem.setIcon(0,act.icon())
                    cmditem.setData(0,Qt.UserRole+1,item)
                    cmditem.setData(0,Qt.UserRole+2,num)
                    items.addChild(cmditem)
                    num += 1
            self.treeWidget.addTopLevelItem(items)
        pass
    def showAllCommand(self):
        self.treeWidget.clear()
        if self.workbench == "Global":
            item = QTreeWidgetItem()
            item.setText(0,"Std")
            items = []
            for cmd in Gui.Command.listAll():
                s = cmd.split('_')
                if s[0] == "Std":
                    cmdobj = Gui.Command.get(cmd)
                    num = 0
                    for act in cmdobj.getAction():
                        cmditem = QTreeWidgetItem()
                        if act.text() == "":
                            continue
                        cmditem.setText(0, act.text())
                        cmditem.setIcon(0, act.icon())

                        cmditem.setData(0, Qt.UserRole + 1, cmd)
                        cmditem.setData(0, Qt.UserRole + 2, num)
                        items.append(cmditem)
                        num += 1
            item.addChildren(items)
            item.setExpanded(True)
            self.treeWidget.addTopLevelItem(item)
        pass

    def getWB(self,wb):
        if wb == "Global":
            Gui.listWorkbenches()
        else:
            return Gui.getWorkbench(wb)

    def onSelectedCommand(self,item,column):
        if item.childCount() > 0:
            return
        self.setProperty("command",item.data(0,Qt.UserRole+1))
        self.setProperty("index", item.data(0,Qt.UserRole + 2))
        self.done(QDialog.Accepted)
        pass

class PMButtonCtl(QPushButton):
    def __init__(self,pos,parent = None):
        super().__init__(parent)
        self.position = pos
        self.clicked.connect(self.onclicked)
        pass

    def onclicked(self):
        if hasattr(self,"menu_path"):
            sel = PMCommandSelector(Gui.getMainWindow(),self.wb)
            if sel.exec_() == QDialog.Accepted:
                strcmd = sel.property("command")
                index = sel.property("index")
                cmd = Gui.Command.get(strcmd)
                act = cmd.getAction()[index]
                param = App.ParamGet(self.menu_path)
                param.SetString("Command_"+str(self.position),strcmd+'-'+str(index))
                self.setText(act.text())
                self.setIcon(act.icon())

            else:
                print('None Selected by Command ')

    def clearCommand(self):
        if hasattr(self,"menu_path"):
            print(self.menu_path)
            param = App.ParamGet(self.menu_path)
            param.RemString("Command_"+str(self.position))
            self.setText("<None>")
            self.setIcon(QIcon())

    def clearData(self):
        self.menu_path = ""
        self.setText("<None>")
        self.setIcon(QIcon())

    def updateCommand(self,wb,menu_path):
        self.wb = wb
        self.menu_path = menu_path
        param = App.ParamGet(menu_path)
        s = param.GetString("Command_"+str(self.position))
        if s != '':
            res = s.split('-')
            scmd = Gui.Command.get(res[0])
            act = scmd.getAction()[int(res[1])]
            self.setText(act.text())
            self.setIcon(act.icon())
        else:
            self.setText("<None>")

class PMKeymapCapture(QKeySequenceEdit):
    KeymapComplete = Signal(QKeySequence)
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        k = self.keySequence()
        self.setKeySequence(k)
        if k.toString() != "":
            self.clearFocus()
            self.KeymapComplete.emit(k)
class PMEditor(QWidget):
    pmmgr = None
    lstCmdCtl = []
    lstDisable = []
    cmdbtn = None
    def __init__(self,pmobj):
        super().__init__(mw)

        self.oldwb = Gui.activeWorkbench()

        self.setWindowTitle(titleName)
        self.setWindowIcon(QIcon(icondir+"FreeCAD-logo.svg"))
        self.resize(800,500)
        self.setWindowFlag(Qt.Dialog)
        layout = QVBoxLayout()
        tab = QTabWidget()
        tab.addTab(self.initSetting(),"General");
        tab.addTab(self.initEditor(), "MenuEditor")
        layout.addWidget(tab)
        self.setLayout(layout)

        self.pmmgr = pmobj


    def closeEvent(self, event):
        global editor
        param = App.ParamGet(ParamsRoot + "Setting/")
        param.SetString("CommandStyle", self.cmdstyle.toPlainText())
        param.SetString("LabelStyle", self.labelstyle.toPlainText())
        if self.pmmgr != None:
            self.pmmgr.reloadConfig()
            self.pmmgr.reloadWorkbench()
            print("restart PieMenu2")

        cmd = Gui.Command.get('Std_Workbench')
        num = 0
        for act in cmd.getAction():
            if act.text() == self.oldwb.MenuText:
                Gui.runCommand('Std_Workbench',num)
                break
            num += 1
        editor = None

    def initSetting(self):
        param = App.ParamGet(ParamsRoot + "Setting/")
        setting = QWidget()
        rightlayout = QVBoxLayout()

        self.globalstyle = QCheckBox("Use Global Stylesheet")
        self.globalstyle.setChecked(param.GetBool("GlobalStyle"))
        self.globalstyle.clicked.connect(self.onGlobalStyle)

        rightlayout.addWidget(self.globalstyle)
        rightlayout.addWidget(QLabel("below write PieMenu command panel stylesheet"))
        self.cmdstyle = QTextEdit()
        self.cmdstyle.setText(param.GetString("CommandStyle"))
        rightlayout.addWidget(self.cmdstyle)
        rightlayout.addWidget(QLabel("below write PieMenu center label stylesheet"))
        self.labelstyle = QTextEdit()
        self.labelstyle.setText(param.GetString("LabelStyle"))
        rightlayout.addWidget(self.labelstyle)

        leftlayout = QVBoxLayout()
        self.pm_enable = QCheckBox("Enable PieMenu2")
        self.pm_enable.setChecked(param.GetBool("Enable"))
        self.pm_enable.clicked.connect(self.onPMEnable)
        leftlayout.addWidget(self.pm_enable)

        self.isDebug = QCheckBox("Enable Keymap Debug")
        self.isDebug.clicked.connect(self.onOpenDebug)
        self.isDebug.setChecked(param.GetBool("KeymapDebug"))
        leftlayout.addWidget(self.isDebug)

        leftlayout.addWidget(QLabel("Set PieMenu2 UI expand radius."))
        sliderlayout = QHBoxLayout()
        sliderlayout.addWidget(QLabel("80"))
        self.radius = QSlider(Qt.Horizontal)
        sliderlayout.addWidget(self.radius)
        self.radius.setMinimum(100)
        self.radius.setMaximum(200)
        curv = param.GetInt("Radius")
        self.radius.setValue(curv)
        self.curvalue = QLabel(str(curv))
        self.radius.valueChanged.connect(self.onRadiusChanged)
        sliderlayout.addWidget(self.curvalue)
        leftlayout.addLayout(sliderlayout)

        leftlayout.addWidget(QLabel("Setting max width value."))
        szlayout = QHBoxLayout()
        v = param.GetInt("maxWidth")
        self.labelmax = QLabel(str(v))
        self.maxwidth = QSlider(Qt.Horizontal)
        self.maxwidth.setMinimum(100)
        self.maxwidth.setMaximum(200)
        self.maxwidth.setValue(v)
        szlayout.addWidget(QLabel(str(self.maxwidth.minimum())))
        szlayout.addWidget(self.maxwidth)
        self.maxwidth.valueChanged.connect(self.onMaxWidthChanged)
        szlayout.addWidget(self.labelmax)

        leftlayout.addLayout(szlayout)
        leftlayout.addStretch()
        leftlayout.setContentsMargins(0,0,20,0)
        rightlayout.setContentsMargins(20,0,0,0)
        layout = QHBoxLayout()
        layout.addLayout(leftlayout)
        layout.addLayout(rightlayout)
        setting.setLayout(layout)
        return setting

    def onMaxWidthChanged(self,v):
        param = App.ParamGet(ParamsRoot + "Setting/")
        param.SetInt("maxWidth", v)
        self.labelmax.setText(str(v))
        pass
    def onGlobalStyle(self):
        path = ParamsRoot + "Setting/"
        param = App.ParamGet(path)
        b = self.globalstyle.isChecked()
        param.SetBool("GlobalStyle", b)
        self.cmdstyle.setDisabled(b)
        self.labelstyle.setDisabled(b)

    def onOpenDebug(self):
        path = ParamsRoot + "Setting/"
        param = App.ParamGet(path)
        param.SetBool("KeymapDebug", self.isDebug.isChecked())

    def onPMEnable(self):
        path = ParamsRoot + "Setting/"
        param = App.ParamGet(path)
        param.SetBool("Enable",self.pm_enable.isChecked())

    def onRadiusChanged(self,value):
        param = App.ParamGet(ParamsRoot + "Setting/")
        param.SetInt("Radius", value)
        self.curvalue.setText(str(value))
    def initEditor(self):
        self.edit = QWidget()
        layout = QHBoxLayout()
        rightlayout = QVBoxLayout()

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignRight)
        self.keymap = PMKeymapCapture()
        self.keymap.setFocusPolicy(Qt.NoFocus)
        self.keymap.KeymapComplete.connect(self.keymapEditComplete)
        klayout = QHBoxLayout()
        klayout.addWidget(self.keymap)

        self.keybtn = QPushButton("RecordKey")
        self.keybtn.clicked.connect(self.keymapCapture)
        self.lstDisable.append(self.keybtn)
        klayout.addWidget(self.keybtn)
        form.addRow("TriggerKey:", klayout)

        self.rule = QLineEdit()
        self.rule.editingFinished.connect(self.onRuleEditFinish)
        self.lstDisable.append(self.rule)
        form.addRow("TriggerRule:",self.rule)
        rightlayout.addLayout(form)

        self.popmode = QRadioButton("PressTrigger")
        self.popmode.clicked.connect(self.onTriggerMode)
        self.lstDisable.append(self.popmode)

        self.clickmode = QRadioButton("ClickTrigger")
        self.clickmode.clicked.connect(self.onTriggerMode)
        self.lstDisable.append(self.clickmode)

        playout = QHBoxLayout()
        playout.addWidget(self.popmode)
        playout.addWidget(self.clickmode)
        form.addRow(None,playout)

        for i in range(8):
            cmdlayout = QHBoxLayout()
            direction = QToolButton()
            direction.setIcon(QIcon(icondir+icons[i]))
            direction.setIconSize(QSize(24,24))
            cmdlayout.addWidget(direction)
            cmdctl = PMButtonCtl(i)
            cmdctl.setText("<None>")
            cmdlayout.addWidget(cmdctl)
            rembtn = QToolButton()
            rembtn.setIcon(QIcon(icondir+"PieMenuRemove.svg"))
            rembtn.setIconSize(QSize(24,24))
            rembtn.clicked.connect(cmdctl.clearCommand)
            self.lstDisable.append(rembtn)
            cmdlayout.addWidget(rembtn)
            self.lstCmdCtl.append(cmdctl)
            rightlayout.addLayout(cmdlayout)

        leftlayout = QVBoxLayout()
        leftlayout.setContentsMargins(0,0,10,0)
        layout.addLayout(leftlayout)

        rightlayout.setContentsMargins(10, 0, 0, 0)
        layout.addLayout(rightlayout)

        self.menutree = QTreeWidget(self.edit)
        self.menutree.setHeaderHidden(True)
        self.menutree.currentItemChanged.connect(self.onMenuChanged)
        self.menutree.itemDoubleClicked.connect(self.onItemDbClick)
        self.menutree.itemChanged.connect(self.onItemChanged)
        self.menutree.itemClicked.connect(self.onItemClick)

        self.addpm = self.AddIconButton(self.edit,"PieMenuAdd.svg",25,self.onAddTopMenu)
        self.addpm.setToolTip("add a top menu.")
        self.addchild = self.AddIconButton(self.edit, "PieMenuAdd.svg", 25, self.onAddChildMenu)
        self.addchild.setToolTip("add a sub menu.")
        self.rempm = self.AddIconButton(self.edit,"PieMenuRemove.svg",25,self.onRemPmClick)
        self.rempm.setToolTip("remove a menu.")
        btnlayout = QHBoxLayout()
        btnlayout.addStretch()
        btnlayout.addWidget(self.addpm)
        btnlayout.addWidget(self.addchild)
        btnlayout.addWidget(self.rempm)
        self.combo = QComboBox(self.edit)
        self.combo.currentIndexChanged.connect(self.onComboCurrentindex)
        cmd = Gui.Command.get('Std_Workbench')
        num = 0
        for act in cmd.getAction():
            self.combo.addItem(QIcon(act.icon()),act.text(),num)
            num += 1
        self.combo.addItem(QIcon(icondir+"FreeCAD-logo.svg"),"Global",num+1)
        self.combo.setCurrentIndex(self.combo.count()-1)
        leftlayout.addWidget(self.combo)
        leftlayout.addLayout(btnlayout)
        leftlayout.addWidget(self.menutree)
        self.edit.setLayout(layout)
        return self.edit


    def DisableMenuEdit(self,d):
        for item in self.lstDisable:
            item.setDisabled(d)
        for item in self.lstCmdCtl:
            if(d == True):
                item.clearData()
            item.setDisabled(d)
    def onTriggerMode(self):
        if self.pmenu != None:
            param = App.ParamGet(self.pmenu)
            if self.popmode.isChecked():
                param.SetString("TriggerMode","Press")
            if self.clickmode.isChecked():
                param.SetString("TriggerMode", "Click")

    def onRuleEditFinish(self):
        item = self.menutree.currentItem()
        if item != None and item.parent() != None:
            if self.pmenu != None:
                param = App.ParamGet(self.pmenu)
                param.SetString("TriggerRule", self.rule.text())

    def onAddTopMenu(self):
        item = self.addPieMenu(ParamsRoot + "Menus/" + self.wb + "/")
        self.menutree.addTopLevelItem(item)
    def onAddChildMenu(self):
        #if self.wb == "Global":
        #    return
        item = self.menutree.currentItem()
        if item != None:
            num = 1
            cur = item
            while True:
                cur = cur.parent()
                if cur == None:
                    break
                num += 1

            if num < 3:
                item.addChild(self.addPieMenu(item.data(0,Qt.UserRole+10)))
                item.setExpanded(True)

    def addPieMenu(self,path):
        title, okPressed = QInputDialog.getText(self, "NewMenuName", "Please input menu name:", QLineEdit.Normal)
        if not okPressed or title == "":
            return
        base = path
        param = App.ParamGet(base)
        if param.HasGroup(title):
            QMessageBox.information(None, "menu already exist!")
            return
        item = QTreeWidgetItem()
        item.setText(0, str(title))
        data = base + title + '/'
        item.setData(0, Qt.UserRole + 10, data)
        item.setCheckState(0, Qt.Unchecked)
        pm = App.ParamGet(base + title)
        self.pmenu = base + title
        pm.SetString("TriggerMode", "Press")
        return item

    def onRemPmClick(self):
        item = self.menutree.currentItem()
        if item != None:
            data = item.data(0, Qt.UserRole + 10)
            param = App.ParamGet(data)
            par = item.parent()
            if par != None:
                par.takeChild(par.indexOfChild(item))
            else:
                self.menutree.takeTopLevelItem(self.menutree.indexOfTopLevelItem(item))
            param.Parent().RemGroup(item.text(0))

    def keymapCapture(self):
        self.keymap.setFocus()

    def keymapEditComplete(self,newkeymap):
        if self.pmenu != None:
            param = App.ParamGet(self.pmenu)
            param.SetString("TriggerKey",newkeymap.toString())


    def AddIconButton(self,parent,icon,iconsize,func):
        btn = QPushButton(parent)
        btn.setIcon(QIcon(icondir + icon))
        btn.setIconSize(QSize(iconsize,iconsize))
        btn.clicked.connect(func)
        return btn

    def getWB(self,index):
        name = self.combo.itemText(index)
        workbench = "Global"
        for k, v in Gui.listWorkbenches().items():
            if v.MenuText == name:
                Gui.runCommand("Std_Workbench", self.combo.itemData(index))
                workbench = k
        return workbench

    def reloadPieMenu(self):
        self.menutree.clear()
        path = ParamsRoot + "Menus/" + self.wb + "/"
        res = self.loadPieMenu(path)
        if res != None:
            self.menutree.addTopLevelItems(res)
            self.menutree.setCurrentItem(res[0])

    def loadPieMenu(self,base):
        pm = App.ParamGet(base)
        grp = pm.GetGroups()
        if len(grp) == 0:
            return None
        treeitem = []
        for item in grp:
            titem = QTreeWidgetItem()
            titem.setText(0, item)
            path = base + item + '/'
            titem.setData(0,Qt.UserRole+10,path)
            p = App.ParamGet(path)
            b = p.GetBool('Enable')
            titem.setCheckState(0, Qt.Checked if b == True else Qt.Unchecked)
            res = self.loadPieMenu(path)
            if res != None:
                titem.addChildren(res)
            treeitem.append(titem)
        return treeitem

    def onItemClick(self,item,_):
        path = item.data(0,Qt.UserRole+10)
        pm = App.ParamGet(path)
        pm.SetBool('Enable',True if item.checkState(_) == Qt.Checked else False)


    def onItemDbClick(self,item,column):
        #item = QTreeWidgetItem()
        #item.setFlags(item.flags() | Qt.ItemIsEditable)
        pass

    def onItemChanged(self,item,column):
        pass
    def onMenuChanged(self,item):
        if item != None:
            self.DisableMenuEdit(False)
            self.pmenu = item.data(0,Qt.UserRole+10)

            for cmd in self.lstCmdCtl:
                cmd.setIcon(QIcon())
                cmd.updateCommand(self.wb,self.pmenu)

            param = App.ParamGet(self.pmenu)
            self.keymap.setKeySequence(QKeySequence(param.GetString("TriggerKey")))
            self.rule.setText(param.GetString("TriggerRule"))
            tm = param.GetString("TriggerMode")
            if tm == "Press":
                self.popmode.setChecked(True)
                self.clickmode.setChecked(False)
            else:
                self.clickmode.setChecked(True)
                self.popmode.setChecked(False)

            if item.parent() == None:
                self.rule.setDisabled(True)
                self.keymap.setDisabled(False)
                self.keybtn.setDisabled(False)
            else:
                self.keymap.setDisabled(True)
                self.keybtn.setDisabled(True)
                self.rule.setDisabled(False)
        else:
            self.DisableMenuEdit(True)

    def onComboCurrentindex(self,index):
        self.wb = self.getWB(index)
        self.reloadPieMenu()
        #self.addchild.setDisabled(self.wb == "Global")



def showPMenuEditor(pmmgr):
    global editor
    editor = PMEditor(pmmgr)
    editor.show()

def hidePMenuEditor():
    global editor
    editor.hide()
    editor = None

