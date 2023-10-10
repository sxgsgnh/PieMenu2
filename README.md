# PieMenu2
为FreeCAD开发的仿blender PieMenu 插件，完全重写了[PieMenu](https://github.com/triplus/PieMenu)的代码，除了uiloader部分。

## 安装

复制PieMenu2文件夹到对应操作系统FreeCAD模块路径下
安装前可能需要删除[PieMenu](https://github.com/triplus/PieMenu)

#### 例子:

Linux:

`/home/user/.FreeCAD/Mod/PieMenu2/InitGui.py`

macOS:

`/Users/user_name/Library/Preferences/FreeCAD/Mod/PieMenu2/InitGui.py`

Windows:

`C:\Users\user_name\AppData\Roaming\FreeCAD\Mod\PieMenu2\InitGui.py`

## 用法
使用方法基本与blender的piemenu一样。  
触发方式分为两种“press”和“click”,一种是按下触发键菜单显示抬起触发键菜单隐藏，另一种是点击触发键菜单显示再次点击该键菜单隐藏，弹出的方式可以在菜单编辑器设置。      
在菜单显示期间按钮高亮的同时弹起触发键隐藏菜单，命令自动执行，或者通过鼠标左键点击对应的菜单按钮执行命令，点击 鼠标右键隐藏菜单

#### 菜单设置
##### 菜单编辑器通用设置
Enable keymap debug <br>   勾选每次点击按键在控制台输出对应的热键，没有则说明触发键与freecad默认热键有冲突需要在FreeCAD中取消对应的热键。</br>
Set PieMenu2 ui expand radius <br>显示菜单圆的半径  
Setting max width value <br>设置菜单按钮的最大宽度，按钮文本超过最大宽度则用省略号代替  </br>
Use Global Stylesheet <br>   勾选使用FreeCAD主题样式，取消使用输入框编写的自定义样式  </br>
##### 菜单编辑器编辑菜单
触发键设置只在根菜单有效。  
<br>   每个触发键菜单是一个由三层的菜单树组成，第一层为根菜单，第二层为对象菜单(由FreeCAD `SelectionObject.ObjectName`属性决定)，第三层为子元素菜单(由FreeCAD `SelectionObject.SubElementNames`属性决定)，当点击触发键时会按照规则弹出对应的菜单或子菜单。</br>
<br>   默认根菜单的TriggerRule禁用不能有属性，第二第三层可以在TriggerRule输入框填写对应的规则，第二层的TriggerRule可以用“ \* ”代替来表示匹配任何选择的对象，如果TriggerRule对象后面跟一个“ + ”号意思是匹配多选，意思是当选择的对象大于一个时候匹配的菜单，菜单匹配优先为确定的对象，如果未找到则查找“ * ”匹配任何对象的菜单，如果都未找到则不弹出菜单。</br>   
<br>   菜单分为全局菜单和工作台菜单，全局菜单不受工作台影响，在全局有效，工作台菜单只在当前工作台下有效  
菜单的TriggerRule在对象前可用视图名加:(视图名由：`Gui.activeView()`确定)来限定在哪个视图下弹出菜单，如果为空默认是3d视图。</br>   
<br> 菜单命令设置则点击对应的命令按钮弹出命令选择器来选择，左侧图标表示该命令出现在菜单ui的具体位置
复选框用来表示是否禁用这个菜单，如果禁用，规则匹配则忽略该菜单不会弹出
按“+，-”图标按钮来添加或删除菜单。</br> 
