""" A script to traverse the database and report objects which are not indexed
in the portal_catalog
"""

from OFS.interfaces import IFolder
from Products.Archetypes.interfaces import IBaseObject
from collections import deque
from persistent.interfaces import IPersistent
from plone.app.discussion.interfaces import IConversation
from zope.annotation.interfaces import IAttributeAnnotatable


def is_ok(Id):
    """ Should the Id be reported as missing?
    """
    if Id.endswith('Criterion'):
        return False
    if Id.endswith('Criteria'):
        return False
    if 'enquiries' in Id:
        return False
    return True


def _children_archetypes(tree, debug=False):
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

    for obj in _children_archetypes(context, debug=False):
        if not hasattr(obj, 'UID'):
            continue
        if not catalog.searchResults(UID=obj.UID()):
            missing.append(obj)

    for obj in missing:
        print obj.absolute_url()

    return [obj.absolute_url() for obj in missing]


def _children_all(tree, debug=False):
    """returns a list of every child"""

    objects = [o for o in tree.objectValues() if IPersistent.providedBy(o)]

    child_list = []
    to_crawl = deque(objects)

    i = 0
    while to_crawl:
        current = to_crawl.popleft()
        child_list.append(current)
        #print "Looking at ", current.absolute_url()
        print ".",

        if IFolder.providedBy(current):
            node_children = [o for o in current.objectValues() if \
                    IAttributeAnnotatable.providedBy(o) and is_ok(o.getId())]
            to_crawl.extend(node_children)

        i += 1
        if debug and (i > 1000):
            break

    return child_list


def reindex_unindexed(self):
    """ reindex objects which are not indexed
    """

    for obj in _children_all(self, debug=False):
        annot = getattr(obj, "__annotations__", {})
        if annot.get("plone.app.discussion:conversation"):
            comments = IConversation(obj)
            for comment in comments.values():
                comment.reindexObject()
                print "Reindexing: ", comment

    return "Done"
