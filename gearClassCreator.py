from maya import cmds


class Gear(object):
    """
    This is a gear object that lets us create and modify gear.
    """

    def __init__(self):
        # run whenever a new instance is created
        self.transform = None
        self.constructor = None
        self.extrude = None

    def createGear(self, teeth=10, length=5):
        spans = teeth * 2
        self.transform, self.constructor = cmds.polyPipe(sa=spans)

        sidefaces = range(spans * 2, spans * 3, 2)

        cmds.select(clear=True)

        for face in sidefaces:
            cmds.select("%s.f[%s]" % (self.transform, face), add=True)

        self.extrude = cmds.polyExtrudeFacet(ltz=length)[0]

    def modifyTeeth(self, teeth=20, length=10):
        spans = teeth * 2

        # get the construction node to reset it
        cmds.polyPipe(self.constructor, edit=True, sa=spans)

        sidefaces = range(spans * 2, spans * 3, 2)
        facenames = []

        # get string list like ['f[40]','f[42]','f[44]']

        for face in sidefaces:
            facename = 'f[%s]' % face
            facenames.append(facename)

        # need more time to think this setAttr()
        # for this case, we change extrude.inputComponents with some new index
        # and some info from Maya Help:
        # Variable length array of components
        # Value Syntax	int {string}
        # Value Meaning	numberOfComponents {componentName}
        # Mel Example	setAttr node.componentListAttr -type componentList 3 cv[1] cv[12] cv[3];
        # Python Example	cmds.setAttr('node.componentListAttr',3,'cv[1]','cv[12]','cv[3]',type='componentList')

        cmds.setAttr('%s.inputComponents' % self.extrude,
                     len(facenames),
                     *facenames,
                     type="componentList")

        # set new variable for this new input component(faces)
        cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=length)
        print facenames

        return None


class gearWindow(object):
    """
    This is a gear window which could create or refresh gear mesh
    """

    def __init__(self):
        self.lengthslider = None
        self.numberslider = None
        self.windowName = "GearWindow"
        self.gear = None

    def show(self):
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)

        self.buildUI()
        cmds.showWindow()

    def buildUI(self):
        column = cmds.columnLayout()
        self.numberslider = cmds.intSliderGrp(field=True, label='teeth number', minValue=3, maxValue=20, value=10)
        self.lengthslider = cmds.intSliderGrp(field=True, label='teeth length', minValue=1, maxValue=20, value=1)

        cmds.rowLayout(numberOfColumns=2)
        cmds.button(label="Create", command=self.createGear)
        cmds.button(label="Refresh", command=self.refreshGear)

        cmds.setParent(column)
        cmds.button(label="Close", command=self.close)

    def close(self, *args):
        cmds.deleteUI(self.windowName)

    def createGear(self, *args):
        teeth = cmds.intSliderGrp(self.numberslider, query=True, value=True)
        length = cmds.intSliderGrp(self.lengthslider, query=True, value=True)
        self.gear = Gear()
        self.gear.createGear(teeth,length)

    def refreshGear(self, *args):
        if self.gear:
            # In query mode, return type is based on queried flag.
            teeth = cmds.intSliderGrp(self.numberslider, query=True, value=True)
            length = cmds.intSliderGrp(self.lengthslider, query=True, value=True)

            self.gear.modifyTeeth(teeth, length)
