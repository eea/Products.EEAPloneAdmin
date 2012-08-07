""" Migrate relations from one object to another
"""

from zope.component import queryAdapter
from Products.CMFCore.utils import getToolByName
from eea.dataservice.relations import IRelations

# Logging
import logging
logger = logging.getLogger('EEAPloneAdmin.migrateRelations')
info = logger.info
info_exception = logger.exception


def migrateRelations(self, old_ob_path, new_ob_path):
    """ Migrate relations from one object to another
    """
    context = self
    old_ob = None
    new_ob = None
    info('INFO: starting relations migration for object %s' % (old_ob_path))
    cat = getToolByName(context, 'portal_catalog')

    query = {'path': {'query': old_ob_path, 'depth': 0}}
    brains = cat(**query)

    if len(brains)>0:
        old_ob = brains[0].getObject()

    query = {'path': {'query': new_ob_path, 'depth': 0}}
    brains = cat(**query)

    if len(brains)>0:
        new_ob = brains[0].getObject()

    # Move all the forward relations to the new_ob.
    forwards = old_ob.getRelatedItems()
    info('INFO: forward relations for object: %s' % (forwards))

    if forwards:
        new_ob.setRelatedItems(forwards)
        old_ob.setRelatedItems([])
        info('INFO: copying forward relations to new object')

    # Take all back refs (objects that refer to old_ob)
    # and make them point to new_ob
    backs = []
    backs_topro = []
    relations = queryAdapter(old_ob, IRelations)
    if relations:
        backs = relations.backReferences()
        #get also back references from other non standard relation field
        backs_topro = relations.backReferences(relatesTo='relatesToProducts')
        info('INFO: standard back refs: %s' % (backs))
        info('INFO: relatesToProducts back refs: %s' % (backs_topro))

    for ob in backs:
        related = ob.getRelatedItems()
        info('INFO: BEFORE updating standard relations on backrefs: %s' % (related))
        #remove reference to old_ob
        del related[related.index(old_ob)]
        related.append(new_ob)
        ob.setRelatedItems(related)
        info('INFO: AFTER updating standard relations on backrefs: %s' % (related))

    for ob in backs_topro:
        related = ob.getRelatedProducts()
        info('INFO: BEFORE updating relatedProducts on backrefs: %s' % (related))
        #remove reference to old_ob
        del related[related.index(old_ob)]
        related.append(new_ob)
        ob.setRelatedProducts(related)
        info('INFO: AFTER updating relatedProducts on backrefs: %s' % (related))

    info('INFO: finished migrating relations')
