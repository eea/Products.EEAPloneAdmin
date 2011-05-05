from DateTime import DateTime
from Globals import DTMLFile
from Products.CMFCore.utils import getToolByName

#from Products.CMFPlone.CatalogTool import CatalogTool

#_enabled = []

#def AlreadyApplied(patch):
    #if patch in _enabled:
        #return True
    #_enabled.append(patch)
    #return False

#def AnonymousCatalog():
    #if AlreadyApplied('AnonymousCatalog'):
        #return

    #CatalogTool.__eeaold_searchResults = CatalogTool.searchResults
    #CatalogTool.searchResults = searchResults
    #CatalogTool.__call__ = searchResults
    #CatalogTool.manage_catalogView = DTMLFile('www/catalogView',globals())

#AnonymousCatalog()


view = DTMLFile('www/catalogView',globals())


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
                             
    return self._old_searchResults(REQUEST, **kw)

