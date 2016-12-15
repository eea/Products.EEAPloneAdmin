""" Patching plone.app.search to strip keyword values
    of non alphanumeric characters
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.ZCTextIndex.ParseTree import ParseError
from Products.CMFPlone.PloneBatch import Batch
from plone.app.contentlisting.interfaces import IContentListing
import re


class Search(BrowserView):

    valid_keys = ('sort_on', 'sort_order', 'sort_limit', 'fq', 'fl', 'facet')

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
        # 79924 patch values in order to avoid bad values
        p = re.compile(r"[^A-Za-z0-9-_]+")
        for k, v in query.items():
            if k == 'SearchableText':
                continue
            if p.match(v):
                query[k] = re.sub(p, v)
        query = self.filter_query(query)

        if query is None:
            results = []
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            try:
                results = catalog(**query)
            except ParseError:
                return []

        results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, b_start)
        return results
