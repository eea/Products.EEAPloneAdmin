""" Patch for plone.app.folder
"""
import plone.app.folder.nogopip

def traverse(base, path):
    """simplified fast unrestricted traverse.

    base: the root to start from
    path: absolute path from app root as string
    returns: content at the end or None
    """
    current = base
    for cid in path.split('/'):
        if not cid:
            continue
        try:
            value = current[cid]
            if value:
                current = value
            else:
                current = current.get(cid)
        except KeyError:
            return None
    return current

plone.app.folder.nogopip.traverse = traverse