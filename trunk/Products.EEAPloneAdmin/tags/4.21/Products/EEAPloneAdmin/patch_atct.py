""" Monkey patches for ATCT
"""

from Products.CMFCore.utils import getToolByName

def listSubtopics(self):
    """Return a list of our subtopics.
    """
    val = self.objectValues(self.meta_type)
    check_p = getToolByName(self, 'portal_membership').checkPermission
    tops = []
    for top in val:
        if check_p('View', top):
            tops.append((top.Title().lower(), top))
    tops.sort()
    tops = [t[1] for t in tops]
    return tops


from OFS.Folder import Folder
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder

ATFolder.manage_options = Folder.manage_options
ATBTreeFolder.manage_options = Folder.manage_options
