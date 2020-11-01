import os
import sd
import json
import random
from os.path import expanduser

from PySide2 import QtGui
from PySide2.QtCore import Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QVBoxLayout, QWidget, QFileDialog, QAction

from sd.api import sdproperty
from sd.ui.graphgrid import GraphGrid
from sd.api.sdproperty import SDPropertyInheritanceMethod

from sd.api.sdgraphobjectframe import SDGraphObjectFrame
from sd.api.sdgraphobjectcomment import SDGraphObjectComment

from  sd.api.sdvalueint import SDValueInt
from  sd.api.sdvalueint2 import SDValueInt2
from  sd.api.sdvalueint3 import SDValueInt3
from  sd.api.sdvalueint4 import SDValueInt4
from sd.api.sdvaluefloat import SDValueFloat
from sd.api.sdvaluefloat2 import SDValueFloat2
from sd.api.sdvaluefloat3 import SDValueFloat3
from sd.api.sdvaluefloat4 import SDValueFloat4
from sd.api.sdvaluebool import SDValueBool
from sd.api.sdvaluebool2 import SDValueBool2
from sd.api.sdvaluebool3 import SDValueBool3
from sd.api.sdvaluebool4 import SDValueBool4
from sd.api.sdtypeenum import SDTypeEnum

from sd.api.sdbasetypes import int2, int3, int4, float2, float3, float4, bool2, bool3, bool4, ColorRGBA

#------------------ AUXILIARY FUNCTIONS ------------------
def getQt():
    ctx = sd.getContext()
    app = ctx.getSDApplication()
    uiMgr = app.getQtForPythonUIMgr()
    return ctx, app, uiMgr

def shortcutAvailable(shortcut, label):
    ctx, app, uiMgr = getQt()
    window = uiMgr.getMainWindow()

    count = 0
    actions = window.findChildren(QAction)
    for ac in actions:
        if ac.shortcut().toString().lower() == shortcut.lower():
            count = -1

    if count is not -1:
        menu = uiMgr.findMenuFromObjectName("mnu_keyshortcut")
        actions = menu.findChildren(QAction)
        for ac in actions:
        	if ac.shortcut().toString().lower() == shortcut.lower() and ac.shortcut().toString().lower() != label.lower():
        		count += 1

    return count

def getShortcutsFile():
    __currdir__ = os.path.dirname(__file__)
    settingsPath = os.path.join(__currdir__,"config/shortcuts.json")

    shortcuts = []
    with open(settingsPath, 'r') as f:
        shortcuts = json.load(f)
    return shortcuts

def saveShortcutsFile(shortcuts):
    settings = []
    for item in shortcuts:
        settings.append(item['widget'].getValue())

    writeShortcutsFile(settings)

def writeShortcutsFile(shortcuts):
    __currdir__ = os.path.dirname(__file__)
    settingsPath = os.path.join(__currdir__,"config/shortcuts.json")
    with open(settingsPath, 'w') as outfile:
        json.dump(shortcuts, outfile)

def createMenu(uiMgr):
    menu = uiMgr.newMenu("",'mnu_keyshortcut')
    shortcuts = getShortcutsFile()
    for item in shortcuts:
        action = menu.addAction(item['label'])
        action.setShortcut(QtGui.QKeySequence(item['key']))
        action.triggered.connect(lambda f=exec_shortcut,arg=item:f(arg))

def getOrigin(selected):
    x = selected[0].getPosition()[0]
    y = selected[0].getPosition()[1]
    for node in selected:
        pos = node.getPosition()
        if pos[0] > x:
            x = pos[0]
            y = pos[1]
    return(x, y)

def getMin(selected):
    x = selected[0].getPosition()[0]
    y = selected[0].getPosition()[1]
    for node in selected:
        pos = node.getPosition()
        if pos[0] < x:
            x = pos[0]
        if pos[1] < y:
            y = pos[1]
    return(x, y)

def getMax(selected):
    x = selected[0].getPosition()[0]
    y = selected[0].getPosition()[1]
    for node in selected:
        pos = node.getPosition()
        if pos[0] > x:
            x = pos[0]
        if pos[1] > y:
            y = pos[1]
    return(x, y)

#------------------ UI CLASSES ------------------
class ExportUI(QWidget):

    def __init__(self):
        super(ExportUI, self).__init__()
        self.__loadUI()

    def __loadUI(self):
        __currdir__ = os.path.dirname(__file__)
        uiPath = os.path.join(__currdir__,"ui/export.ui")
        self.widget = QUiLoader().load(uiPath)
        self.lyt_main = QVBoxLayout()
        self.setLayout(self.lyt_main)
        self.lyt_main.addWidget(self.widget)

        self.widget.btn_path.clicked.connect(lambda:self.__btnPathClick(self.widget.btn_path))

    def __btnPathClick(self, btn):
        ctx = sd.getContext()
        app = ctx.getSDApplication()
        uiMgr = app.getQtForPythonUIMgr()
        window = uiMgr.getMainWindow()
        fileName = QFileDialog.getExistingDirectory(window, "Open a folder", expanduser("~"), QFileDialog.ShowDirsOnly)
        if fileName:
            self.widget.txt_path.setText(fileName)

    def setValue(self, item):
        self.widget.lbl_name.setText(item['label'])
        self.widget.txt_key.setText(item['key'])
        self.widget.txt_path.setText(item['path'])
        self.widget.cmb_ext.setCurrentIndex(item['idx'])
        self.item = item

    def getValue(self):
        self.item['key'] = self.widget.txt_key.text()
        self.item['path'] = self.widget.txt_path.text()
        self.item['ext'] = self.widget.cmb_ext.currentText()
        self.item['idx'] = self.widget.cmb_ext.currentIndex()
        self.item.pop('widget', None)
        return self.item


class FrameUI(QWidget):

    def __init__(self):
        super(FrameUI, self).__init__()
        self.__loadUI()

    def __loadUI(self):
        __currdir__ = os.path.dirname(__file__)
        uiPath = os.path.join(__currdir__,"ui/frame.ui")
        self.widget = QUiLoader().load(uiPath)
        self.lyt_main = QVBoxLayout()
        self.setLayout(self.lyt_main)
        self.lyt_main.addWidget(self.widget)


    def setValue(self, item):
        self.widget.lbl_name.setText(item['label'])
        self.widget.txt_key.setText(item['key'])
        self.widget.txt_r.setValue(item['color'][0])
        self.widget.txt_g.setValue(item['color'][1])
        self.widget.txt_b.setValue(item['color'][2])
        self.widget.txt_a.setValue(item['alpha'])
        if item['rand'] == 1:
            self.widget.chk_rand.setChecked(True)
        else:
            self.widget.chk_rand.setChecked(False)
        self.item = item

    def getValue(self):
        self.item['key'] = self.widget.txt_key.text()
        self.item['alpha'] = self.widget.txt_a.value ()
        self.item['color'] = [self.widget.txt_r.value(), self.widget.txt_g.value(), self.widget.txt_b.value()]
        if self.widget.chk_rand.isChecked():
            self.item['rand'] = 1
        else:
            self.item['rand'] = 0
        self.item.pop('widget', None)
        return self.item


class ShortcutUI(QWidget):
    def __init__(self):
        super(ShortcutUI, self).__init__()
        self.__loadUI()

    def __loadUI(self):
        __currdir__ = os.path.dirname(__file__)
        uiPath = os.path.join(__currdir__,"ui/shortcut.ui")
        self.widget = QUiLoader().load(uiPath)
        self.lyt_main = QVBoxLayout()
        self.setLayout(self.lyt_main)
        self.lyt_main.addWidget(self.widget)


    def setValue(self, item):
        self.widget.lbl_name.setText(item['label'])
        self.widget.txt_key.setText(item['key'])
        self.item = item

    def getValue(self):
        self.item['key'] = self.widget.txt_key.text()
        self.item.pop('widget', None)
        return self.item


class NodeUI(QWidget):
    def __init__(self):
        super(NodeUI, self).__init__()
        self.__loadUI()
        self.item = None
    def __loadUI(self):
        __currdir__ = os.path.dirname(__file__)
        uiPath = os.path.join(__currdir__,"ui/node.ui")
        self.widget = QUiLoader().load(uiPath)
        self.lyt_main = QVBoxLayout()
        self.setLayout(self.lyt_main)
        self.lyt_main.addWidget(self.widget)

        self.widget.txt_key.textChanged.connect(self.__textChanged)

    def __textChanged(self):
        if self.item is not None:
            self.__isValid()

    def __isValid(self):
        exist = shortcutAvailable(self.widget.txt_key.text(), self.item['label'])
        print("label: "+self.item['label'] + " name: " + self.item['name'] + " shortcut:"+ self.item['key'] +" exist = %d"%exist)
        if exist == -1:
            self.widget.txt_key.setStyleSheet("background-color: #4E0707;")
        elif exist > 1:
            self.widget.txt_key.setStyleSheet("background-color: #4E0707;")
        else:
            self.widget.txt_key.setStyleSheet("background-color: #252525;")


    def setValue(self, item):
        self.widget.lbl_name.setText(item['name'])
        self.widget.txt_key.setText(item['key'])
        self.widget.txt_src.setText(item['src'])
        self.item = item
        self.__isValid()

    def getValue(self):
        self.item['key'] = self.widget.txt_key.text()
        self.item['name'] = self.widget.lbl_name.text()
        self.item.pop('widget', None)
        return self.item


class MainUI(QWidget):

    def __init__(self):
        super(MainUI, self).__init__()
        self.shortcuts = []
        self.__loadUI()

    def __loadUI(self):
        __currdir__ = os.path.dirname(__file__)
        uiPath = os.path.join(__currdir__,"ui/main.ui")
        self.widget = QUiLoader().load(uiPath)
        self.lyt_shortcuts = QVBoxLayout()
        self.lyt_shortcuts.setAlignment(Qt.AlignTop)
        self.lyt_shortcuts.setSpacing(0)
        self.widget.scr_shortcuts.setLayout(self.lyt_shortcuts)

        self.widget.btn_save.clicked.connect(lambda:self.__btnSaveClick(self.widget.btn_save))
        self.widget.btn_reset.clicked.connect(lambda:self.__btnResetClick(self.widget.btn_reset))
        self.widget.btn_addNode.clicked.connect(lambda:self.__btnaddNodeClick(self.widget.btn_addNode))

        self.__getShortcuts()

    def __btnSaveClick(self, btn):
        saveShortcutsFile(self.shortcuts)
        uiMgr = getQt()[2]
        window = uiMgr.getMainWindow()
        uiMgr.deleteMenu("mnu_keyshortcut")
        createMenu(uiMgr)

        self.shortcuts = []
        items = self.widget.scr_shortcuts.findChildren(QWidget)
        for item in items:
            item.setParent(None)
            #TODO: add delete widget
        self.__getShortcuts()

    def __btnResetClick(self, btn):
        uiMgr = getQt()[2]
        window = uiMgr.getMainWindow()

        self.shortcuts = []
        items = self.widget.scr_shortcuts.findChildren(QWidget)
        for item in items:
            item.setParent(None)
            #TODO: add delete widget
        self.__getShortcuts()

    def __btnaddNodeClick(self, btn):
        ctx, app, uiMgr = getQt()
        #Graph exists
        try:
            graph = uiMgr.getCurrentGraph()
        except:
            print ("ERROR: No graph active")
            return

        #Node selected
        selection = uiMgr.getCurrentGraphSelection()
        if len(selection) < 1:
            print ("ERROR: No node selected")
            return

        node = selection[0]
        props = []
        for prop in node.getProperties(sd.api.sdproperty.SDPropertyCategory.Input):
            if not prop.isConnectable():
                try:
                    value = node.getInputPropertyValueFromId(prop.getId())
                except:
                    value = None

                if value is not None:
                    init_val = 0
                    type = prop.getType().getId()
                    if prop.getType().getId() == 'int':
                        init_val = value.get()
                    elif prop.getType().getId() == 'int2':
                        init_val = [value.get().x, value.get().y]
                    elif prop.getType().getId() == 'int3':
                        init_val = [value.get().x, value.get().y, value.get().z]
                    elif prop.getType().getId() == 'int4':
                        init_val =  [value.get().w, value.get().x, value.get().y, value.get().z]
                    elif prop.getType().getId() == 'float':
                        init_val = value.get()
                    elif prop.getType().getId() == 'float2':
                        init_val =  [value.get().x, value.get().y]
                    elif prop.getType().getId() == 'float3':
                        init_val =  [value.get().x, value.get().y, value.get().z]
                    elif prop.getType().getId() == 'float4':
                        init_val = [value.get().w, value.get().x, value.get().y, value.get().z]
                    elif prop.getType().getId() == 'bool':
                        init_val = value.get()
                    if  isinstance(prop.getType(), SDTypeEnum):
                        init_val = value.get()
                        type = "enum"

                    if prop.getId().find("$") > -1:
                        data = node.getPropertyInheritanceMethod(prop)
                        inheritance = 0
                        if data == SDPropertyInheritanceMethod.RelativeToParent :
                            inheritance = 1
                        elif data == SDPropertyInheritanceMethod.Absolute:
                            inheritance = 2
                    else:
                        inheritance = -1

                    props.append({"id":prop.getId(), "value":init_val, "type":type, "inheritance":inheritance})

        if node.getDefinition().getId() == 'sbs::compositing::sbscompgraph_instance':
            pkgMgr = app.getPackageMgr()
            url = node.getReferencedResource().getUrl()
            resource = None
            file = ""
            for pkg in pkgMgr.getPackages():
                resource = pkg.findResourceFromUrl(url)
                if resource:
                    file = pkg.getFilePath()

            if not resource:
                print("ERROR: resource not found")
                return
            newVal = {"type": "NODE_CUSTOM", "label": "Add Node", "key": "", "src": node.getReferencedResource().getUrl(), "name": node.getDefinition().getLabel(), "file":file ,"props":props}
        else:
            newVal = {"type": "NODE", "label": "Add Node", "key": "", "src": node.getDefinition().getId(), "name": node.getDefinition().getLabel(), "props":props}

        saveShortcutsFile(self.shortcuts)
        list = getShortcutsFile()
        list.append(newVal)
        writeShortcutsFile(list)
        self.__btnResetClick(None)


    def __getShortcuts(self):
        self.shortcuts = getShortcutsFile()
        idx = 0
        for item in self.shortcuts:
            if item['type'] == "NODE" or item['type'] == "NODE_CUSTOM":
                widget = NodeUI()
                widget.widget.btn_del.clicked.connect(lambda f=self.__btnDelClick,arg=idx:f(arg))
            elif item['type'] == "FRAME":
                widget = FrameUI()
            elif item['type'] == "EXPORT":
                widget = ExportUI()
            else:
                widget = ShortcutUI()

            widget.setValue(item)
            item['widget'] = widget
            self.lyt_shortcuts.addWidget(widget)
            self.lyt_shortcuts.setAlignment(widget, Qt.AlignTop)
            idx += 1

    def __btnDelClick(self, idx):
        saveShortcutsFile(self.shortcuts)
        list = getShortcutsFile()
        del list[idx]
        writeShortcutsFile(list)
        self.__btnResetClick(None)


#------------------ SHORTCUT EXECUTION ------------------
def exec_shortcut(item):
    if item['type'] == 'NODE' or item['type'] == 'NODE_CUSTOM':
        addNode(item)
    elif item['type'] == 'FRAME':
        addFrame(item)
    elif item['type'] == 'COMMENT':
        addComment(item)
    elif item['type'] == 'EXPORT':
        exportNodes(item)
    elif item['type'] == 'RANDOM':
        setRandomSeed(item)

def exportNodes(item):
    uiMgr = getQt()[2]
    window = uiMgr.getMainWindow()
    try:
        graph = uiMgr.getCurrentGraph()
    except:
        print ("ERROR: No graph active")
        return

    selection = uiMgr.getCurrentGraphSelection()
    if len(selection) == 0:
        print("ERROR: No nodes selected")
        return
    elif len(selection) == 1:
        fileName = QFileDialog.getSaveFileName(window, 'Export Current Map', item['path'], selectedFilter='*.'+item['ext'])
        if fileName and fileName[0] is not '':
            noExt = fileName[0].replace('.' + item['ext'], '')
            filePath = noExt + "." + item['ext']
            exportImages(graph, selection[0], filePath)

    else:
        fileName = QFileDialog.getSaveFileName(window, 'Export Current Map', item['path'], selectedFilter='*.'+item['ext'])
        if fileName and fileName[0] is not '':
            idx = 0
            for node in selection:
                noExt = fileName[0].replace('.' + item['ext'], '')
                filePath = noExt + "_" + str(idx) + "." + item['ext']
                idx +=1
                exportImages(graph, node, filePath)

def exportImages(graph,node,filePath):
    graph.compute()
    outputProperties = node.getDefinition().getProperties(sdproperty.SDPropertyCategory.Output)
    for outputProperty in outputProperties:
        propertyValue = node.getPropertyValue(outputProperty)
        # Get the property value as texture
        propertyTexture = propertyValue.get()
        if not propertyTexture:
            continue

        try:
            propertyTexture.save(filePath)
            print('Texture saved to: %s' % filePath)
        except APIException:
            print('Fail to save texture %s' % filePath)

        return filePath

def addFrame(item):
    uiMgr = getQt()[2]
    cGridSize = GraphGrid.sGetFirstLevelSize()
    try:
        graph = uiMgr.getCurrentGraph()
    except:
        print ("ERROR: No graph active")
        return

    frame = SDGraphObjectFrame.sNew(graph)
    frame.setTitle('Title')
    frame.setDescription('Description')

    if item['rand'] == 1:
        #TODO: adjust size and pos based on selection
        frame.setColor(ColorRGBA(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), item['alpha']))
    else:
        frame.setColor(ColorRGBA(item['color'][0], item['color'][1], item['color'][2], item['alpha']))

    selection = uiMgr.getCurrentGraphSelection()
    if len(selection) > 0:
        min = getMin(selection)
        max = getMax(selection)

        size = [max[0]- min[0], max[1]- min[1]]
        frame.setPosition(float2(min[0] -cGridSize, min[1] -cGridSize))
        frame.setSize(float2(size[0] + cGridSize * 2, size[1] + cGridSize * 2))
    else:
        frame.setPosition(float2(-cGridSize, -cGridSize))
        frame.setSize(float2(2*cGridSize, 2*cGridSize))

def addComment(item):
    uiMgr = getQt()[2]
    cGridSize = GraphGrid.sGetFirstLevelSize()
    try:
        graph = uiMgr.getCurrentGraph()
    except:
        print ("ERROR: No graph active")
        return

    selection = uiMgr.getCurrentGraphSelection()
    if len(selection) > 0:
        comment = SDGraphObjectComment.sNewAsChild(selection[0])
        comment.setPosition(float2(-cGridSize*0.5, cGridSize*0.5))
        comment.setDescription('Comment')

    else:
        comment = SDGraphObjectComment.sNew(graph)
        comment.setPosition(float2(-cGridSize*0.5, cGridSize*0.5))
        comment.setDescription('Comment')

def setRandomSeed(item):
    uiMgr = getQt()[2]
    cGridSize = GraphGrid.sGetFirstLevelSize()
    try:
        graph = uiMgr.getCurrentGraph()
    except:
        print ("ERROR: No graph active")
        return

    selection = uiMgr.getCurrentGraphSelection()
    for node in selection:
        rand = int(random.uniform(0, 1) * 999999999)
        value = SDValueInt.sNew(rand)
        node.setInputPropertyValueFromId("$randomseed", value)

def addNode(item):
    ctx, app, uiMgr = getQt()
    cGridSize = GraphGrid.sGetFirstLevelSize()

    try:
        graph = uiMgr.getCurrentGraph()
    except:
        print ("ERROR: No graph active")
        return

    if item["type"] == "NODE":
        node = graph.newNode(item['src'])
    else:
        url = item['src']
        pkgMgr = app.getPackageMgr()
        pkg = pkgMgr.loadUserPackage(item["file"])
        resource = pkg.findResourceFromUrl(url.split("?")[0])
        print(item["file"],resource,url.split("?")[0])
        node = graph.newInstanceNode(resource)
        #pkgMgr.unloadUserPackage(pkg)

    for prop in item['props']:
        value = None
        if prop["type"] == 'int':
            value = SDValueInt.sNew(prop["value"])
        elif prop["type"] == 'int2':
            value = SDValueInt2.sNew(int2(prop["value"][0], prop["value"][1]))
        elif prop["type"] == 'int3':
            value = SDValueInt3.sNew(int3(prop["value"][0], prop["value"][1], prop["value"][2]))
        elif prop["type"] == 'int4':
            value = SDValueInt4.sNew(int4(prop["value"][0], prop["value"][1], prop["value"][2], prop["value"][3]))
        elif prop["type"] == 'float':
            value = SDValueFloat.sNew(prop["value"])
        elif prop["type"] == 'float2':
            value = SDValueFloat2.sNew(float2(prop["value"][0], prop["value"][1]))
        elif prop["type"] == 'float3':
            value = SDValueFloat3.sNew(float3(prop["value"][0], prop["value"][1], prop["value"][2]))
        elif prop["type"] == 'float4':
            value = SDValueFloat4.sNew(float4(prop["value"][0], prop["value"][1], prop["value"][2], prop["value"][3]))
        elif prop["type"] == 'bool':
            value = SDValueBool.sNew(prop["value"])
        elif prop["type"] == 'enum':
            value = SDValueInt.sNew(prop["value"])

        if value is not None:
            if prop["inheritance"] != -1:
                inheritance = SDPropertyInheritanceMethod.RelativeToInput
                if prop['inheritance'] == 1 :
                    inheritance = SDPropertyInheritanceMethod.RelativeToParent
                elif prop['inheritance'] == 2:
                    inheritance = SDPropertyInheritanceMethod.Absolute
                node.setInputPropertyInheritanceMethodFromId(prop["id"], inheritance)

            node.setInputPropertyValueFromId(prop["id"], value)

    selection = uiMgr.getCurrentGraphSelection()
    if len(selection) > 0:
        origin = getOrigin(selection)
        node.setPosition(float2(origin[0] + cGridSize * 1.5, origin[1]))


#------------------ PLUGIN INITIALIZATION ------------------
def initializeSDPlugin():
    uiMgr = getQt()[2]
    createMenu(uiMgr)

    widget = uiMgr.newDockWidget('sd_shortcuts','Shortcut Manager')
    lyt_main = QVBoxLayout()
    widget.setLayout(lyt_main)
    main_ui = MainUI()
    widget.layout().addWidget(main_ui.widget)


def uninitializeSDPlugin():
    pass
