from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import keyframeEditor as kf
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from maya import cmds


def getMayaMainWindow():
    """
    This function will return the pointer of Maya main window
    So our UI window can set it as parent
    """

    # give us back the memory address of the main window
    # So we need to convert this to something our Python libraries will understand
    win = omui.MQtUtil_mainWindow()

    # convert this memory address into a long integer
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


class KeyframeEditorUI(QtWidgets.QWidget):
    def __init__(self):
        # Set its parent as Maya main window
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        layout = QtWidgets.QVBoxLayout(parent)

        super(KeyframeEditorUI, self).__init__(parent=parent)

        self.setWindowTitle('Keyframe Editor')
        self.setFixedWidth(600)
        self.setFixedHeight(100)
        self.buildUI()

        # add widget to the parent layout
        self.parent().layout().addWidget(self)
        parent.show()

    def buildUI(self):
        main_layout = QtWidgets.QGridLayout(self)

        # a label to show the current offset value
        self.info = QtWidgets.QLabel('Time Offset')
        main_layout.addWidget(self.info)
        main_layout.addWidget(self.info, 0, 1)

        # a slider to assign desired offset value
        self.slidernum = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slidernum.setMinimum(-999)
        self.slidernum.setMaximum(999)
        self.slidernum.setSingleStep(1)
        self.slidernum.setValue(0)
        self.slidernum.valueChanged.connect(lambda val: self.textnum.setText(str(val)))
        main_layout.addWidget(self.slidernum, 0, 2, 1, 3)

        #
        self.textnum=QtWidgets.QLineEdit()
        self.textnum.setMaximumWidth(100)
        self.textnum.setText(str(self.slidernum.value()))
        self.textnum.textChanged.connect(lambda val: self.slidernum.setValue(int(val)))
        main_layout.addWidget(self.textnum, 0, 5)

        # a button for 'Set Selected'
        setselectedbtn = QtWidgets.QPushButton('Set Selected')
        setselectedbtn.setMaximumWidth(200)
        setselectedbtn.clicked.connect(partial(self.setAnimCurveTimeOffset, selection=True))
        main_layout.addWidget(setselectedbtn, 1, 3)

        # a button for 'Set All'
        setallbtn = QtWidgets.QPushButton('Set All')
        setallbtn.setMaximumWidth(200)
        setallbtn.clicked.connect(partial(self.setAnimCurveTimeOffset, selection=False))
        main_layout.addWidget(setallbtn, 1, 4)

        # a button to reset offset value as zero
        resetbtn = QtWidgets.QPushButton('Reset')
        resetbtn.setMaximumWidth(200)
        resetbtn.clicked.connect(self.resetOffset)
        main_layout.addWidget(resetbtn, 1, 5)

    def setAnimCurveTimeOffset(self,selection=True):
        num = 0
        anim_curve = kf.getAllAnimCurveWithTimeAsInput(selection=selection)
        num = kf.setKeyframesTimeOffset(anim_curve, self.slidernum.value())
        self.slidernum.setValue(0)

        # pop a window to show the info of execution
        cmds.confirmDialog(title='Output', message="The number of curves which have been moved: %s." % num, button='Close')
        return num

    def resetOffset(self):
        self.slidernum.setValue(0)
        self.textnum.setText('0')

