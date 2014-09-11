""" Detect faceted navigation objects using Subject as criteria
"""
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger('EEAPloneAdmin.find_search_areas_using_subjects')
info = logger.info
info_exception = logger.exception

def find_faceted_navigation(self):
    """ Detect faceted navigation objects using Subject as criteria
        and return a detailed report
    """
    faceted_interface = \
         'eea.facetednavigation.subtypes.interfaces.IFacetedNavigable'
    context = self
    cat = getToolByName(context, 'portal_catalog')
    result = {}

    brains = cat.unrestrictedSearchResults(object_provides=faceted_interface)

    #count = 1
    for brain in brains:
        obj = brain.getObject()
        query = obj.restrictedTraverse('faceted_query')
        xml = query.criteria()
        if 'Subject' in xml.keys():
            result[obj.absolute_url()] = xml['Subject']['query']

    info('Done searching for facetednav with Subject as criteria')
    return result
