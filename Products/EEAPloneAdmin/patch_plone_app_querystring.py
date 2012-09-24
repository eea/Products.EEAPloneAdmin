""" Plone.app.querystring patches
"""
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.querystring import queryparser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
# patch imports
from zope.site.hooks import getSite

def _makequery(self, query=None, batch=False, b_start=0, b_size=30,
                sort_on=None, sort_order=None, limit=0, brains=False):
    """Parse the (form)query and return using multi-adapter"""
    parsedquery = queryparser.parseFormquery(
        self.context, query, sort_on, sort_order)
    if not parsedquery:
        if brains:
            return []
        else:
            return IContentListing([])

    catalog = getToolByName(self.context, 'portal_catalog')
    if batch:
        parsedquery['b_start'] = b_start
        parsedquery['b_size'] = b_size
    elif limit:
        parsedquery['sort_limit'] = limit

    # original code
    #if 'path' not in parsedquery:
    #    parsedquery['path'] = {'query': ''}
    #parsedquery['path']['query'] = getNavigationRoot(self.context) + \
    #        parsedquery['path']['query']

    # patch
    if 'path' not in parsedquery:
        parsedquery['path'] = {'query': ''}
    site = getSite()
    site_path = "/".join(site.getPhysicalPath())
    parsedquery['path']['query'] = site_path + parsedquery['path']['query']
    # end patch

    results = catalog(parsedquery)
    if not brains:
        results = IContentListing(results)
    if batch:
        results = Batch(results, b_size, b_start)
    return results
