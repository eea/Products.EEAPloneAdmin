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
