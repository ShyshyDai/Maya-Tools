from maya import cmds
import logging

logging.basicConfig()
logger = logging.getLogger('keyframeEditor')
logger.setLevel(logging.DEBUG)


def setKeyframesTimeOffset(anim_curve=None, time=0):
    """
    This function will move all the given curves along the timeline with certain distance.
    Args:
        anim_curve: the curve which will be moved
        time: offset value

    Returns: the number of curves which have been moved successfully

    """
    num = 0
    if not anim_curve:
        logger.error("There is no anim curve selected!")
    else:
        num = cmds.keyframe(anim_curve, time=(), edit=True, timeChange=time, relative=True)

    logger.info("The number of curves which have been moved: %s." % num)

    return num


def getAllAnimCurveWithTimeAsInput(obj=None, selection=True):
    """
    This function will get all the anim curves which take time as input.

    Args:
        obj: objects which anim curves would be searched from
        selection: only valid when obj param is none. True- with objects selected currently; False- with all the objects in the current scene.

    Returns: a list of anim curves

    """

    anim_curve = []

    if not obj:
        if not selection:
            # select all the objects in the scene
            obj = cmds.ls(dag=True)
        else:
            # get objects which have been selected (including attributes)
            obj = cmds.selectionConnection('graphEditor1FromOutliner', q=True, object=True)

    logger.debug(obj)

    anim_curve.extend(getAnimCurveFromObj(obj, curve_type='animCurveTA'))
    anim_curve.extend(getAnimCurveFromObj(obj, curve_type='animCurveTU'))
    anim_curve.extend(getAnimCurveFromObj(obj, curve_type='animCurveTL'))
    anim_curve.extend(getAnimCurveFromObj(obj, curve_type='animCurveTT'))

    return anim_curve


def getAnimCurveFromObj(obj, curve_type='animCurve'):
    """
    This function will return specified type of anim curves
    Args:
        obj: where the anim curves come from
        curve_type: the specified type of anim curves

    Returns: a list of anim curves

    """
    anim_curve = []

    # This obj could also be some attributes
    # Note: Attribute Name is like "pSphere1.rotateY" and Curve Name is like "pSphere1_rotateY"
    curves = cmds.listConnections(obj, type=curve_type)

    if curves:
        # Note: list.extend(None) will arise error
        anim_curve.extend(curves)

    return anim_curve
