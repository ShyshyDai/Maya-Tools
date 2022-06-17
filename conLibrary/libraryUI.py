from maya import cmds
import pprint

# here, if the statement is "from Qt import QtWidgets, QtCore, QtGui"
# PyCharm will be confused to this abstract library
# and will mark something as unidentifiable
# for easy coding(like autocomplete), we use PySide2 here
# (lose the benefit of using qt abstraction layer of course)
from PySide2 import QtWidgets, QtCore, QtGui
import controllerLibrary
reload(controllerLibrary)

'''
Next:
* a default image that is displayed when there is no screenshot
* put controller to a certain position(like constrain to something)
* check about the repeat controller name and give a warning
'''


class ControllerLibraryUI(QtWidgets.QDialog):
    """
    The ControllerLibraryUI is a dialog to save or import controller.
    """
    def __init__(self):
        # execute  init function in its parent(s) class
        super(ControllerLibraryUI, self).__init__()

        self.setWindowTitle('Controller Library UI')

        # an instance for controller library
        self.library = controllerLibrary.ControllerLibrary()

        # Everytime we create a new instance, we will build the UI and populate it
        self.buildUI()
        self.populate()

    def buildUI(self):
        # QVBoxLayout is short for QVerticalLayout
        # and this is the master layout
        layout = QtWidgets.QVBoxLayout(self)

        # the save region, including an input column and save button
        # and you can see, in Qt, whenever you want to set the layout
        # you have to assign the widget
        # while for maya cmds, it adds everything to the last layout created
        saveWidget = QtWidgets.QWidget()
        saveLayout = QtWidgets.QHBoxLayout(saveWidget)

        # add the saveWidget to the framework
        layout.addWidget(saveWidget)

        # add an input field to the saveLayout
        self.saveNameField = QtWidgets.QLineEdit()
        saveLayout.addWidget(self.saveNameField)

        # add a button to the saveLayout
        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.save)
        saveLayout.addWidget(saveBtn)

        # the field for gallery view of controller
        picsize = 64
        buffersize = 12
        self.listWidget = QtWidgets.QListWidget()
        # set view-mode as icon-mode
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        # QWidget,QtCore,QGui?
        self.listWidget.setIconSize(QtCore.QSize(picsize, picsize))
        # set resize mode as adjust
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.listWidget.setGridSize(QtCore.QSize(picsize + buffersize, picsize + buffersize))

        layout.addWidget(self.listWidget)

        # three buttons on the bottom
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        layout.addWidget(btnWidget)

        importBtn = QtWidgets.QPushButton('Import')
        importBtn.clicked.connect(self.load)
        btnLayout.addWidget(importBtn)

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate)
        btnLayout.addWidget(refreshBtn)

        closeBtn = QtWidgets.QPushButton('Close')
        # close() is a built-in function
        closeBtn.clicked.connect(self.close)
        btnLayout.addWidget(closeBtn)

    def populate(self):
        """This function will clear current list widget and repopulates it with the contents of controller library."""

        self.listWidget.clear()
        self.library.find()

        for name, info in self.library.items():
            # like a sub layer
            item = QtWidgets.QListWidgetItem(name)
            self.listWidget.addItem(item)

            screenshot = info.get('screenshot')
            if screenshot:
                icon = QtGui.QIcon(screenshot)
                item.setIcon(icon)

            item.setToolTip(pprint.pformat(info))

    def load(self):
        """This function will load the current selected item to the scene."""
        # Get current item selected
        currentitem = self.listWidget.currentItem()
        if not currentitem:
            cmds.warning("No item selected!")
        else:
            name = currentitem.text()
            self.library.load(name)

    def save(self):
        """This function will save controller with certain name."""
        name = self.saveNameField.text()
        if not name.strip():
            cmds.warning("You have to give a name!")
        else:
            self.library.save(name)
            self.populate()
            self.saveNameField.setText('')


def showUI():
    """
    This function shows and returns a handle to the ui.
    Returns:
        QDialog

    """
    ui = ControllerLibraryUI()
    ui.show()
    print ui
    return ui
