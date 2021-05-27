""" Use collective.taxonomy instead of portal_vocabulary for faceted objects
"""
import logging
import transaction
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import queryAdapter
from zope.component.interface import interfaceToName
from persistent.list import PersistentList
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.config import ANNO_CRITERIA


logger = logging.getLogger("Products.EEAPloneAdmin")


def change_faceted_vocabularies(context):
    """ Use collective.taxonomy taxonomies instead of portal_vocabulary
    """
    catalog = getToolByName(context, 'portal_catalog')
    iface = interfaceToName(context, IFacetedNavigable)
    brains = catalog.unrestrictedSearchResults(object_provides=iface)

    vocabularies = {
        'themes': 'collective.taxonomy.themes',
        'themesmerged': 'collective.taxonomy.themesmerged'
    }

    count = 0
    for brain in brains:
        doc = brain.getObject()
        anno = queryAdapter(doc, IAnnotations)
        criterias = anno.get(ANNO_CRITERIA, '')

        for crit in criterias:
            if crit.vocabulary in vocabularies.keys():
                logger.info(
                    "Modified %s vocabulary for %s", crit.vocabulary, doc.absolute_url()
                )
                crit.vocabulary = vocabularies[crit.vocabulary]                
                count += 1

        anno[ANNO_CRITERIA] = PersistentList(criterias)
    transaction.commit()
    logger.info("Modified %s vocabularies.", count)