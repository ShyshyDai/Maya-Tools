import os
import json
import time
from Qt import QtWidgets, QtGui, QtCore
import pymel.core as pm
from functools import partial
# import OpenMaya API to access Maya's UI elements
from maya import OpenMayaUI as omui
# build portable code:
import Qt
import logging

##################################
# Todo:
# 1. Modify the onSolo method to make sure only one light can be soloed at once.
# 2. Use the stylesheets to give the buttons some color to spice it up a bit.
# 3. Let the user choose where to save the lights file to.
#################################

logging.basicConfig()
logger = logging.getLogger('LightingManager')

# This library lets us define many outputs and many levels
# When we release our code for other people to use, we can disable some lower logging levels
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)

# This library (Qt) has a variable that lets us know which binding it is using under the hood
if Qt.__binding__ == 'PySide':
    logger.debug('Using PySide with Shiboken')
    # shiboken is a library for pyside that converts qt elements into pyside elements
    from Shiboken import wrapInstance
    # The QtCore.Signal is different between PyQt and PySide
    from Qt.QtCore import Signal
    # if it is PyQt
elif Qt.__binding__.startswith('PyQt'):
    logger.debug('Using PyQt with sip')
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
else:
    # for PySide2
    from shiboken2 import wrapInstance

    logger.debug('Using PySide2 with Shiboken')
    from Qt.QtCore import Signal

def getMayaMainWindow():
    """
    This function will return the pointer of Maya main window
    So our LightManager window can set it as parent
    """

    # give us back the memory address of the main window
    # So we need to convert this to something our Python libraries will understand
    win = omui.MQtUtil_mainWindow()

    # ptr is short for pointer
    # convert this memory address into a long integer
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


def getDock(name='LightingManagerDock'):
    """
    This function will create a dock window in the main window.
    Args:
        name: the name of the dock window

    Returns: pointer of the dock window

    """
    delDock()
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Lighting Manager")
    qtCtrl = omui.MQtUtil_findControl(ctrl)

    # convert it to QWidget
    ptr = wrapInstance(long(qtCtrl), QtWidgets.QWidget)
    return ptr


def delDock(name='LightingManagerDock'):
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)


class LightManager(QtWidgets.QWidget):
    """

    """
    LightTypes = {
        "Point Light": pm.pointLight,
        "Spot Light": pm.spotLight,
        "Directional Light": pm.directionalLight,
        "Ambient Light": pm.ambientLight,

        # no pm.areaLight ?
        "Area Light": partial(pm.shadingNode, 'areaLight', asLight=True),
        "Volume Light": partial(pm.shadingNode, 'volumeLight', asLight=True)
    }

    def __init__(self, dock=True):

        # make it optional
        if dock:
            parent = getDock()
        else:
            delDock()

            # try-except:
            # if the try statement is wrong
            # the except statement will be trigger
            # and continue on the rest of code
            try:
                pm.deleteUI('LightingManager')
            except:
                logger.debug('No previous UI exists')
            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            # so maya can look up this control through its name
            parent.setObjectName('LightingManager')
            layout = QtWidgets.QVBoxLayout(parent)

        super(LightManager, self).__init__(parent=parent)
        self.lightTypeCB = None
        self.scrollLayout = None
        self.setWindowTitle('Light Manager')
        self.buildUI()
        self.populate()

        # add widget to the parent layout
        self.parent().layout().addWidget(self)

        # Maya dock will show its window automatically
        # while QDialog not, so:
        if not dock:
            parent.show()

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)

        self.lightTypeCB = QtWidgets.QComboBox()
        for lighttype in sorted(self.LightTypes):
            self.lightTypeCB.addItem(lighttype)

        layout.addWidget(self.lightTypeCB, 0, 0,1,2)

        createBtn = QtWidgets.QPushButton('Create')
        createBtn.setMaximumWidth(80)
        createBtn.clicked.connect(self.createLight)
        layout.addWidget(createBtn, 0, 2)

        scrollWidget = QtWidgets.QWidget()

        # so the distance between each lightwidget will be limited
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)
        layout.addWidget(scrollArea, 1, 0, 1, 3)

        saveBtn=QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.save)
        saveBtn.setMaximumWidth(100)
        layout.addWidget(saveBtn,2,0)

        importBtn=QtWidgets.QPushButton('Import')
        importBtn.clicked.connect(self.importLight)
        importBtn.setMaximumWidth(100)
        layout.addWidget(importBtn,2,1)

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate)
        saveBtn.setMaximumWidth(100)
        layout.addWidget(refreshBtn, 2, 2)

    def save(self):
        properties={}

        for lightWidget in self.findChildren(LightWidget):
            light = lightWidget.light
            transform=light.getTransform()

            properties[str(transform)]={
                # Vector we get back from PyMel are not directly convertible into something that json can understand
                # So we need to do some shift for it
                'translate':list(transform.translate.get()),
                'rotate':list(transform.rotate.get()),
                'type':pm.objectType(light),
                'intensity':light.intensity.get(),
                'color':light.color.get()
            }

        directory = self.getDirectory()

        lightFile=os.path.join(directory,'lightFile_%s.json' % time.strftime('%m%d%H%M'))
        with open(lightFile,'w') as f:
            json.dump(properties,f,indent=4)
        logger.info('Saving file to %s' % lightFile)

    def getDirectory(self):

        # This method is generated automatically through "Refactor->Extract Method"
        directory = os.path.join(pm.internalVar(userAppDir=True), 'LightManager')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def importLight(self):
        directory = self.getDirectory()

        # Get the selected file
        # self is its parent
        fileName=QtWidgets.QFileDialog.getOpenFileName(self,"Light Browser",directory)
        with open(fileName[0],'r') as f:
            properties=json.load(f)

        for light,info in properties.items():
            lightType=info.get('type')

            # lightTypes[list] stores type of light as "Area Light"
            # while Json stores it as "areaLight"
            # this is a for-else statement
            for lt in self.LightTypes:
                if '%sLight' % (lt.split()[0].lower()) == lightType:
                    logger.info("Find Corresponding %s in %s" % (lt,lightType))
                    break

            # if the current for-loop is completed with no break
            # then come to the else statement
            else:
                logger.info('Cannot find corresponding light type for %s' % light)
                continue

            light=self.createLight(lt)
            light.intensity.set(info.get('intensity'))
            light.color.set(info.get('color'))

            transform=light.getTransform()
            transform.translate.set(info.get('translate'))
            transform.rotate.set(info.get('rotate'))

            self.populate()

    def populate(self):
        # Clear all first

        # This is PlanA
        #    while self.scrollLayout.count():
        #        # Get item [0] from the layout
        #        widget=self.scrollLayout.takeAt(0).widget()
        #        if widget:
        #            widget.setVisible(False)
        #            widget.deleteLater()

        # This is PlanB
        lightWidgets = self.findChildren(LightWidget)
        for widget in lightWidgets:
            widget.setVisible(False)
            widget.deleteLater()

        # list function in pymel:
        for light in pm.ls(
                type=["areaLight", "spotLight", "pointLight", "directionalLight", "volumeLight", "ambientLight"]):
            self.addLight(light)

    def createLight(self,lighttype=None):
        if not lighttype:
            lighttype = self.lightTypeCB.currentText()

        # Query a function in LightTypes list
        func = self.LightTypes[lighttype]
        light = func()
        self.addLight(light)

        return light

    def addLight(self, light):
        widget = LightWidget(light)
        self.scrollLayout.addWidget(widget)

        # ************** important here *************** #
        # signal slot event receiver sender connect emit disconnect
        widget.onSolo.connect(self.onSolo)

    def onSolo(self, value):

        # find all children with LightWidget type
        lightWidgets = self.findChildren(LightWidget)
        for widget in lightWidgets:

            # if you call this function in a slot, then it will return the source of signal
            if widget != self.sender():
                widget.disableLight(value)


class LightWidget(QtWidgets.QWidget):
    onSolo = Signal(bool)

    def __init__(self, light):
        super(LightWidget, self).__init__()
        self.name = None
        if isinstance(light, basestring):
            light = pm.PyNode(light)
        if isinstance(light,pm.nodetypes.Transform):
            light=light.getShape()

        self.light = light
        self.buildUI()

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)

        # We need the name of Transform instead Shape
        self.name = QtWidgets.QCheckBox(str(self.light.getTransform()))
        self.name.setChecked(self.light.visibility.get())

        # set visibility on transform instead shape
        self.name.toggled.connect(lambda val: self.light.getTransform().visibility.set(val))

        # def setLightVisibility(val):
        #     self.light.visibility.set(val)

        layout.addWidget(self.name, 0, 0)

        soloBtn = QtWidgets.QPushButton('Solo')
        soloBtn.setCheckable(True)
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val))
        layout.addWidget(soloBtn, 0, 1)

        delBtn = QtWidgets.QPushButton('X')
        delBtn.clicked.connect(self.deleteLight)
        delBtn.setMaximumWidth(50)
        layout.addWidget(delBtn, 0, 2)

        intensity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        intensity.setMinimum(1)
        intensity.setMaximum(100)
        intensity.setValue(self.light.intensity.get())
        intensity.valueChanged.connect(lambda val: self.light.intensity.set(val))
        layout.addWidget(intensity, 1, 0, 1, 2)

        self.colorBtn = QtWidgets.QPushButton()
        self.colorBtn.setMaximumWidth(20)
        self.colorBtn.setMaximumHeight(20)
        self.setBtnColor()
        self.colorBtn.clicked.connect(self.setColor)
        layout.addWidget(self.colorBtn, 1, 2)

    def setBtnColor(self, color=None):
        if color == None:
            color = self.light.color.get()

        # The assert statement is used to continue the execute if the given condition evaluates to True.
        # If the assert condition evaluates to False,
        # then it raises the AssertionError exception with the specified error message.
        assert len(color) == 3, "Invalid format: Three float value must be given."

        # In maya, each value in color is stored as [0,1] instead [0,255]
        # List Comprehension again
        r, g, b = [c * 255 for c in color]

        # QSS: (Qt Style Sheet) as well as CSS for website
        self.colorBtn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0)' % (r, g, b))

    def setColor(self):
        lightColor = self.light.color.get()

        # launch color editor
        # something annoying here
        # the return value of color is stored as a string like <unicode> "1 0 0 1"
        # so we need do some special treatment for it
        color = pm.colorEditor(rgbValue=lightColor)
        # List Comprehension again
        r, g, b, a = [float(c) for c in color.split()]
        color = (r, g, b)

        self.light.color.set(color)
        self.setBtnColor(color)

    def disableLight(self, value):
        self.name.setChecked(not value)

    def deleteLight(self):
        # Theoretically you can just run the single call(the final one) and both of these should happen
        # but sometimes Python and qt can conflict and will keep it around
        # so we run all three of these together to keep everything right
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

        pm.delete(self.light.getTransform())


def showUI():
    ui = LightManager()
    ui.show()
    return ui

# Before we set MayaMainWindow as parent,
# we draw the LightManager Window like below:
# ----------------------------------
# ui = LightManager.LightManager()
# ui.showUI()
# ----------------------------------
# While with parent setting, we can show UI directly
# and Maya will treat it as child (no overlap anymore) and keep it active
# ----------------------------------
# LightManager.LightManager().show()
# ----------------------------------
