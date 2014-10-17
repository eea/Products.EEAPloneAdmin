""" A script to traverse the database and report objects which are not indexed
in the portal_catalog
"""

from OFS.interfaces import IFolder
from Products.Archetypes.interfaces import IBaseObject
from collections import deque


def is_ok(id):
    """ Should the id be reported as missing?
    """
    if id.endswith('Criterion'):
        return False
    if id.endswith('Criteria'):
        return False
    if 'enquiries' in id:
        return False
    return True


def _children(tree, debug=False):
    """returns a list of every child"""

    objects = [o for o in tree.objectValues() if IBaseObject.providedBy(o)]

    child_list = []
    to_crawl = deque(objects)

    i = 0
    while to_crawl:
        current = to_crawl.popleft()
        child_list.append(current)
        print "Looking at ", current.absolute_url()

        if IFolder.providedBy(current):
            node_children = [o for o in current.objectValues() if \
                    IBaseObject.providedBy(o) and is_ok(o.getId())]
            to_crawl.extend(node_children)

        i += 1
        if debug and (i > 1000):
            break

    return child_list


def discover_unindexed(self):
    """ Traverse the ZODB and report which objects are not 
    indexed in the catalog
    """
    catalog = self.portal_catalog
    context = self

    missing = []

    for obj in _children(context, debug=False):
        if not hasattr(obj, 'UID'):
            continue
        if not catalog.searchResults(UID=obj.UID()):
            missing.append(obj)

    for obj in missing:
        print obj.absolute_url()

    return [obj.absolute_url() for obj in missing]
