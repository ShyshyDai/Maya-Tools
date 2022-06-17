from maya import cmds
import os
import json
import pprint

USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'controllerLibrary')


def createDirectory(directory=DIRECTORY):
    """
    This function will create a file if the given directory is None
    Args:
        directory:

    Returns:

    """
    if not os.path.exists(directory):
        os.mkdir(directory)


class ControllerLibrary(dict):

    def save(self, name, directory=DIRECTORY, screenshot=True, **info):
        """
        This function will save .ma and corresponding .json file to specified position
        Args:
            name:file name
            directory: the path we store the files
            screenshot:
            **info: a list with arbitrary arguments

        Returns:

        """
        createDirectory(directory)

        path = os.path.join(directory, '%s.ma' % name)
        infopath = os.path.join(directory, '%s.json' % name)

        cmds.file(rename=path)
        info['name'] = name
        info['path'] = path

        if cmds.ls(selection=True):
            cmds.file(force=True, type='mayaAscii', exportSelected=True)
        else:
            cmds.file(save=True, type='mayaAscii', force=True)

        if screenshot:
            self.saveScreenshot(name, directory=DIRECTORY)

        # *python context*
        # some logic will be trigger before and after the command finish
        # in this case, before: check the path and open the file
        # after: save and close the file
        # keep everything simple and safe
        with open(infopath, 'w') as f:
            json.dump(info, f, indent=4)

        self[name] = info

    def find(self, directory=DIRECTORY):
        """
        This Function help us find all the .ma files in the specific directory.
        And their corresponding .json and .jpg files if there are
        Then store these info in controller library(self)

        Args:
            directory:

        Returns:

        """
        self.clear()

        if not os.path.exists(directory):
            print "Nothing here"
            return

        files = os.listdir(directory)
        mayafiles = [f for f in files if f.endswith(".ma")]
        for ma in mayafiles:
            name, ext = os.path.splitext(ma)
            path = os.path.join(directory, ma)

            infopath = '%s.json' % name
            if infopath in files:
                infopath = os.path.join(directory, infopath)

                with open(infopath, 'r') as f:
                    info = json.load(f)
            else:
                info = {}

            screenshot = '%s.jpg' % name
            if screenshot in files:
                info['screenshot'] = os.path.join(directory, screenshot)

            # self is inherited from dict.
            # We set the name as one of the keys
            # and path as the value
            self[name] = info

    def load(self, name):
        path = self[name]['path']
        if path:
            if os.path.exists(path):
                # The namespace name to use that will group all objects during importing and referencing.
                # Change the namespace used to group all the objects from the specified referenced file.
                # The reference must have been created with the "Using Namespaces" option, and must be loaded.
                # Non-referenced nodes contained in the existing namespace will also be moved to the new namespace.
                # "i" is short for import
                cmds.file(path, i=True, usingNamespaces=False)
            else:
                print "Invalid path!"
        else:
            print "no file!"

    def saveScreenshot(self, name, directory=DIRECTORY):
        path = os.path.join(directory, "%s.jpg" % name)

        # The viewFit command positions the specified camera so its point-of-view contains all selected objects other than itself.
        # If no objects are selected, everything is fit to the view (excepting cameras, lights, and sketching planes).
        cmds.viewFit()

        # How'd we get this command?
        # just click "render setting - file output - image format - JPEG(jpg)"
        # then maya will show it in the output window
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

        # showOrnaments: Sets whether model view ornaments (e.g. the axis icon) should be displayed
        # viewer: Specify whether a viewer should be launched for the playblast. Default is "true".
        # Runs "fcheck" when -fmt is "image". The player for movie files depends on the OS:
        # Windows uses Microsoft Media Player, Irix uses movieplayer, OSX uses QuickTime.
        cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=200, height=200,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)

        return path
