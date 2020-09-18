import os      #20200702开始学习插件的制作
import sd



def initializeSDPlugin():
    ctx = sd.getContext()
    app = ctx.getSDApplication()
    uiMgr = app.getQtForPythonUIMgr()

    widget = uiMgr.newDockWidget('jianpingplugin','jianping plugin')
    lyt_main = QVBoxLayout()
    widget.setLayout(lyt_main)

    main_ui = MainUI(uiMgr)
    widget.layout().addWidget(main_ui.widget)

def uninitializeSDPlugin():
    pass
