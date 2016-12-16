""" Patching plone.app.search to strip keyword values
    of non alphanumeric characters
"""
from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError
from Products.CMFPlone.PloneBatch import Batch
from plone.app.contentlisting.interfaces import IContentListing
import re


def results(self, query=None, batch=True, b_size=10, b_start=0):
    """ Get properly wrapped search results from the catalog.
    Everything in Plone that performs searches should go through this view.
    'query' should be a dictionary of catalog parameters.
    """
    if query is None:
        query = {}
    if batch:
        query['b_start'] = b_start = int(b_start)
        query['b_size'] = b_size
    # 79924 patch str values in order to avoid bad values
    # in case it contains non alphabetic characters
    p = re.compile(r"[^A-Za-z0-9-_]+")
    query = self.filter_query(query)
    for k, v in query.items():
        if k == 'SearchableText':
            continue
        if not isinstance(v, basestring):
            continue
        if p.search(v):
            query[k] = re.sub(p, "", v)
        if k == 'sort_on':
            # 79924
            # you should only be allowed to search by date or sortable_title
            # by removing the sort_on key if we have other values passed in
            # we avoid a CatalogError
            if v and v not in ['Date', 'sortable_title']:
                del query[k]

    if query is None:
        res = []
    else:
        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            res = catalog(**query)
        except ParseError:
            return []

    res = IContentListing(res)
    if batch:
        res = Batch(res, b_size, b_start)
    return res
