""" Cataloging related patches
"""

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

HAS_COLLECTIVE_INDEXING = True
try:
    from collective.indexing.queue import processQueue
except ImportError:
    HAS_COLLECTIVE_INDEXING = False


def searchResults(self, REQUEST=None, **kw):
    """ Calls ZCatalog.searchResults with extra arguments that
        limit the results to what the user is allowed to see.

        This version adds state and effective date range for
        anonymous users.
    """
    kw = kw.copy()
    membershipTool = getToolByName(self, 'portal_membership', None)

    if membershipTool.isAnonymousUser():
        kw['review_state'] = 'published'
        kw['effectiveRange'] = DateTime()

    if HAS_COLLECTIVE_INDEXING:
        # flush the queue before querying the catalog
        processQueue()

    return self._old_searchResults(REQUEST, **kw)


#from Globals import DTMLFile
#view = DTMLFile('www/catalogView', globals())

# If parent has more then 50 children reorder will be restricted in order
# to avoid heavy wake up of objects. See more under #2803
#NOTE: we disabled this on plone4 because default method in CMFPlone doesn't
#      do anything anymore

#from Products.CMFCore.permissions import ModifyPortalContent
#from Products.CMFPlone.utils import log
#def reindexOnReorder(self, parent):
    #""" Catalog ordering support """

    #if len(parent.objectIds()) > 50:
        #log('This context has more then 50 children and reorder is \
             #restricted. Path %s' % parent.absolute_url(1))
        #return

    #mtool = getToolByName(self, 'portal_membership')
    #if not mtool.checkPermission(ModifyPortalContent, parent):
        #return

    #cat = getToolByName(self, 'portal_catalog')
    #cataloged_objs = cat(path = {'query':'/'.join(parent.getPhysicalPath()),
                                 #'depth': 1})
    #for brain in cataloged_objs:
        #obj = brain.getObject()
        ## Don't crash when the catalog has contains a stale entry
        #if obj is not None:
            #cat.reindexObject(obj,['getObjPositionInParent'],
                                                #update_metadata=0)
        #else:
            ## Perhaps we should remove the bad entry as well?
            #log('Object in catalog no longer exists, cannot reindex: %s.'%
                                #brain.getPath())

