from maya import cmds


def tween(percentage, obj=None, attrs=None, selection=True):
    """
    This function will help us to create tweener between keys.
    Args:
        percentage: the position of tweener, should be in range of [0,1]
        obj: the object we want to edit with
        attrs: the attrs we want to edit with
        selection: whether to edit object selected or not

    Returns:
        None
    """
    if not obj and not selection:
        # ValueError is one of the error type which is set to RuntimeError as default.
        raise ValueError("No object given to tween!")
    if not obj:
        obj = cmds.ls(selection=True)[0]

    if not attrs:
        attrs = cmds.listAttr(obj, keyable=True)

    # just query this attribute instead change it
    currenttime = cmds.currentTime(query=True)

    for attr in attrs:
        attrfullname = '%s.%s' % (obj, attr)

        # get the list of keyframes
        keyframes = cmds.keyframe(attrfullname, query=True)

        if not keyframes:
            continue

        prevkeyframes = []
        for key in keyframes:
            if key < currenttime:
                prevkeyframes.append(key)

        # list comprehension
        laterkeyframes = [frame for frame in keyframes if frame > currenttime]

        if not prevkeyframes and not laterkeyframes:
            continue

        if prevkeyframes:
            prevframe = max(prevkeyframes)

        else:
            prevframe = None

        # simplify if-else statement
        nextframe = min(laterkeyframes) if laterkeyframes else None

        if not prevframe or not nextframe:
            continue

        prevvalue = cmds.getAttr(attrfullname, time=prevframe)
        nextvalue = cmds.getAttr(attrfullname, time=nextframe)

        different = nextvalue - prevvalue

        weighteddiff = different * percentage
        currentvalue = prevvalue + weighteddiff

        cmds.setKeyframe(attrfullname, time=currenttime, value=currentvalue)
        # print "current value = (%s - %s) * %s + %s" % (nextvalue, prevvalue, percentage, prevframe)

    return None


class tweenWindow(object):
    def __init__(self):
        self.slider = None
        self.windowName = "TweenWindow"

    def show(self):
        # remove the previous one when repeat
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)

        self.buildUI()
        cmds.showWindow()

    def buildUI(self):
        column = cmds.columnLayout()
        cmds.text(label="Use this slide to set the tween amount")

        row = cmds.rowLayout(numberOfColumns=2)

        self.slider = cmds.floatSlider(min=0, max=1, value=0.5, step=0.1, changeCommand=tween)

        # We use command=self.reset instead command=self.reset(),
        # cause we don't want it is executed immediately
        cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.button(label="Close", command=self.close)

    # There is an extra argument
    # cause maya button will also send an extra value to any function that they're calling
    def reset(self, *args):
        cmds.floatSlider(self.slider, edit=True, value=0.5)

    def close(self, *args):
        cmds.deleteUI(self.windowName)
