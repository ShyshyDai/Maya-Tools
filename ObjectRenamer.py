from maya import cmds

SUFFIXES = {
    "mesh": "geo",
    "joint": "jnt",
    "camera": None
}
DEFAULT_SUFFIX = "grp"


def renamer(selection=False):
    """
    Rename the objects with suffix corresponding to their type

    Args:
        selection: Whether we use the objects selected or not

    Returns:
        The object List with new name

    """
    objects = cmds.ls(selection=selection, long=True, dag=True)

    if selection and not objects:
        raise RuntimeError("There is no object selected.")

    else:
        objects.sort(key=len, reverse=True)

        for obj in objects:
            shortname = obj.split('|')[-1]
            children = cmds.listRelatives(obj, children=True) or []

            if len(children) == 1:
                child = children[0]
                objtype = cmds.objectType(child)
            else:
                objtype = cmds.objectType(obj)

            suffix = SUFFIXES.get(object,DEFAULT_SUFFIX)

            if not suffix:
                continue

            if obj.endswith('_' + suffix):
                continue

            else:
                new_name = "%s_%s" % (shortname, suffix)
                cmds.rename(obj, new_name)

                index = objects.index(obj)
                objects[index] = obj.replace(shortname, new_name)

    return objects
