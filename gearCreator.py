from maya import cmds


def createGear(teeth=10, length=5):
    """
    This function will create a gear with ideal teeth num and length.
    Args:
        teeth: the num of teeth
        length: the length of teeth

    Returns:
        the object name and construct node name,as well as extrude node.
    """
    spans = teeth * 2
    transform, constructor = cmds.polyPipe(sa=spans)

    sidefaces = range(spans * 2, spans * 3, 2)

    cmds.select(clear=True)

    for face in sidefaces:
        cmds.select("%s.f[%s]" % (transform, face), add=True)

    extrude = cmds.polyExtrudeFacet(ltz=length)[0]
    print transform, constructor, extrude

    return transform, constructor, extrude


def modifyTeeth(constructor, extrude, teeth=20, length=10):
    """
    This function will modify the existed gear with new setting
    Args:
        constructor: the construction node of gear
        extrude: the related node of gear
        teeth: the num of teeth you want to modify
        length: the length of teeth you want to modify

    Returns:
        None
    """
    spans = teeth * 2

    # get the construction node to reset it
    cmds.polyPipe(constructor, edit=True, sa=spans)

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

    cmds.setAttr('%s.inputComponents' % extrude,
                 len(facenames),
                 *facenames,
                 type="componentList")

    # set new variable for this new input component(faces)
    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)
    print facenames

    return None
